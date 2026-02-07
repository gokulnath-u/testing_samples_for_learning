import math
import multiprocessing as mp
import os
import time


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2

    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True


def nearest_prime(n: int) -> int:
    offset = 0
    while True:
        if offset == 0 and is_prime(n):
            return n

        if n - offset > 1 and is_prime(n - offset):
            return n - offset
        if is_prime(n + offset):
            return n + offset

        offset += 1


def worker(worker_id: int, x: int):
    pid = os.getpid()
    value = x ** 8

    print(f"[Worker {worker_id}] PID={pid} START")
    start = time.time()

    prime = nearest_prime(value)

    end = time.time()
    print(
        f"[Worker {worker_id}] PID={pid} DONE "
        f"in {end - start:.2f}s (digits={len(str(prime))})"
    )


if __name__ == "__main__":
    WORKERS = mp.cpu_count()  # should be 80
    X = 1000                # increase slowly (15000, 20000)

    print(f"Detected CPU threads: {WORKERS}")
    print(f"Spawning {WORKERS} CPU-bound workers\n")

    start_all = time.time()

    with mp.Pool(processes=WORKERS) as pool:
        pool.starmap(worker, [(i, X) for i in range(WORKERS)])

    end_all = time.time()
    print(f"\nALL WORKERS FINISHED in {end_all - start_all:.2f}s")
