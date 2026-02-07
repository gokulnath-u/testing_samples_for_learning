# Lucas-Lehmer-like CPU stress test to stress CPU
import multiprocessing as mp
import os
import time
import signal
import sys

RUN_SECONDS = 120  # stop after 2 minutes


def lucas_lehmer_like(worker_id: int):
    # Smaller but still heavy
    p = 2_000_003   # ~250 KB integers
    M = (1 << p) - 1

    x = 4
    iterations = 0
    start = time.time()

    while time.time() - start < RUN_SECONDS:
        x = (x * x - 2) % M
        iterations += 1

        if iterations % 50 == 0:
            elapsed = time.time() - start
            print(
                f"[Worker {worker_id}] "
                f"Iter={iterations} "
                f"Elapsed={elapsed:.1f}s"
            )

    print(f"[Worker {worker_id}] DONE")


def main():
    workers = os.cpu_count()
    print(f"Starting CPU stress on {workers} processes")

    procs = []
    for i in range(workers):
        p = mp.Process(target=lucas_lehmer_like, args=(i,))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()


if __name__ == "__main__":
    main()
