import os
import time
import logging
import multiprocessing
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(processName)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pipeline.main")


# -------------------------------------------------------------------
# PDF Split
# -------------------------------------------------------------------

def split_pdf(input_pdf: str, output_dir: Path, pages_per_chunk: int):
    doc = fitz.open(input_pdf)
    total_pages = doc.page_count

    logger.info(f"Total pages: {total_pages}")
    logger.info(f"Pages per chunk: {pages_per_chunk}")

    chunk_files = []

    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk, total_pages)

        chunk_doc = fitz.open()
        chunk_doc.insert_pdf(doc, from_page=start, to_page=end - 1)

        chunk_name = f"{Path(input_pdf).stem}_pages_{start+1}_{end}.pdf"
        chunk_path = output_dir / chunk_name

        chunk_doc.save(chunk_path)
        chunk_doc.close()

        chunk_files.append(str(chunk_path))
        logger.info(f"Created chunk: {chunk_name}")

    doc.close()
    logger.info(f"Split complete. Total chunks: {len(chunk_files)}")
    return chunk_files


# -------------------------------------------------------------------
# OCR Worker (separate process)
# -------------------------------------------------------------------

def ocr_worker(file_path: str):
    os.environ["CUDA_VISIBLE_DEVICES"] = ""  # force CPU

    pid = os.getpid()
    worker_logger = logging.getLogger("worker.ocr")

    worker_logger.info(
        f"TASK_START | pid={pid} | file={os.path.basename(file_path)}"
    )

    start = time.time()

    try:
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            do_table_structure=False,
        )

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

        res = converter.convert(file_path)
        markdown = (
            res.document.export_to_markdown()
            if res and res.document
            else ""
        )

        elapsed = time.time() - start

        worker_logger.info(
            f"CHUNK_OCR_OK | pid={pid} | "
            f"file={os.path.basename(file_path)} | "
            f"time={elapsed:.2f}s"
        )

        return {
            "status": "success",
            "file_path": file_path,
            "markdown": markdown,
            "ocr_time": elapsed,
            "pid": pid,
        }

    except Exception as e:
        elapsed = time.time() - start
        worker_logger.exception(
            f"CHUNK_OCR_FAIL | pid={pid} | "
            f"file={file_path} | time={elapsed:.2f}s"
        )

        return {
            "status": "error",
            "file_path": file_path,
            "markdown": "",
            "error": str(e),
            "ocr_time": elapsed,
            "pid": pid,
        }


# -------------------------------------------------------------------
# Merge markdown
# -------------------------------------------------------------------

def merge_markdown_chunks(results, output_file: str):
    logger.info(f"Merging {len(results)} chunks")

    parts = []

    for i, res in enumerate(results, start=1):
        content = res.get("markdown", "")
        if content:
            parts.append(
                f"\n<!-- ===== Chunk {i} ===== -->\n{content}"
            )
        else:
            logger.warning(f"Chunk {i} empty or failed")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    logger.info(f"Merged markdown saved to {output_file}")


# -------------------------------------------------------------------
# Main pipeline
# -------------------------------------------------------------------

def run_pipeline(
    input_pdf: str,
    output_md: str,
    pages_per_chunk: int = 25,
    cpu_target: float = 0.85,   # 80–85% CPU
):
    start_time = time.time()

    total_cpus = multiprocessing.cpu_count()
    max_workers = int(total_cpus * cpu_target)

    logger.info(
        f"CPU_INFO | total_cpus={total_cpus} | "
        f"cpu_target={int(cpu_target*100)}% | "
        f"max_workers={max_workers}"
    )

    chunk_dir = Path("temp_chunks")
    chunk_dir.mkdir(exist_ok=True)

    chunk_files = split_pdf(input_pdf, chunk_dir, pages_per_chunk)
    total_chunks = len(chunk_files)

    effective_workers = min(total_chunks, max_workers)

    logger.info(
        f"CONCURRENCY_PLAN | chunks={total_chunks} | "
        f"workers={effective_workers}"
    )

    results = []

    with ProcessPoolExecutor(max_workers=effective_workers) as executor:
        futures = [
            executor.submit(ocr_worker, chunk)
            for chunk in chunk_files
        ]

        for future in as_completed(futures):
            results.append(future.result())

    merge_markdown_chunks(results, output_md)

    total_time = time.time() - start_time
    logger.info(
        f"PDF_DONE | file={input_pdf} | "
        f"chunks={total_chunks} | time={total_time:.2f}s"
    )

    return total_time


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    input_pdf = "sample/Sample1-ASM.pdf"
    output_md = "sample/md/Sample1-ASM.md"

    if not Path(input_pdf).exists():
        raise FileNotFoundError(input_pdf)

    print(f"Starting OCR pipeline for {input_pdf}")

    duration = run_pipeline(
        input_pdf=input_pdf,
        output_md=output_md,
        pages_per_chunk=50,
        cpu_target=0.85,   # senior-approved 😉
    )

    print(f"Done! Output: {output_md}")
    print(f"Total time: {duration:.2f} seconds")
