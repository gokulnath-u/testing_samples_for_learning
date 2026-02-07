import asyncio
import time
import os
from concurrent.futures import ProcessPoolExecutor

# ---------------------------
# CPU-heavy task (parallel)
# ---------------------------
def cpu_heavy_task(file_id: int):
    print(f"[PID {os.getpid()}] Processing file {file_id}")
    total = 0
    for i in range(20_000_000):
        total += i % 7
    return f"File {file_id} processed"


# ---------------------------
# I/O-bound task (concurrent)
# ---------------------------
async def download_file(file_id: int):
    print(f"Downloading file {file_id}...")
    await asyncio.sleep(1)  # simulate network delay
    return file_id


# ---------------------------
# Combined pipeline
# ---------------------------
async def main():
    start = time.time()

    # 1️⃣ Concurrent downloads (async)
    download_tasks = [download_file(i) for i in range(5)]
    downloaded_files = await asyncio.gather(*download_tasks)

    print("\nAll downloads completed\n")

    # 2️⃣ Parallel CPU processing
    with ProcessPoolExecutor(max_workers=4) as pool:
        loop = asyncio.get_running_loop()

        cpu_tasks = [
            loop.run_in_executor(pool, cpu_heavy_task, file_id)
            for file_id in downloaded_files
        ]

        results = await asyncio.gather(*cpu_tasks)

    print("\nResults:")
    for r in results:
        print(r)

    print(f"\nTotal time taken: {time.time() - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
