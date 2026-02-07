# Monte Carlo Pi estimation – controlled CPU stress (80–85%)
import multiprocessing as mp
import os
import time
import random

RUN_SECONDS = 60
CPU_TARGET = 0.8   # 80% CPU utilization per core
WORK_CYCLE = 0.05  # 50ms cycle for busy/sleep loop


def pi_worker(worker_id: int):
    start_time = time.time()
    inside_circle = 0
    total_points = 0

    print(f"[Worker {worker_id}] START")

    while time.time() - start_time < RUN_SECONDS:
        # Busy phase
        cycle_start = time.time()
        points_this_cycle = 0
        while time.time() - cycle_start < WORK_CYCLE * CPU_TARGET:
            x = random.random()
            y = random.random()
            if x*x + y*y <= 1.0:
                inside_circle += 1
            points_this_cycle += 1

        total_points += points_this_cycle

        # Sleep phase
        sleep_time = WORK_CYCLE * (1 - CPU_TARGET)
        if sleep_time > 0:
            time.sleep(sleep_time)

    pi_est = (inside_circle / total_points) * 4
    print(f"[Worker {worker_id}] DONE | Pi ≈ {pi_est:.5f}")


if __name__ == "__main__":
    total_cpus = os.cpu_count()
    workers = total_cpus  # spawn 1 worker per CPU

    print(f"Detected CPUs       : {total_cpus}")
    print(f"Spawning workers    : {workers} (~{int(CPU_TARGET*100)}% load each)")
    print(f"Run duration        : {RUN_SECONDS}s\n")

    processes = []
    for i in range(workers):
        p = mp.Process(target=pi_worker, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("\nAll workers finished cleanly.")
