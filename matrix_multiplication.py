# matrix multiplication stress test to stress CPU
import multiprocessing as mp
import os
import time
import random

RUN_SECONDS = 60 
MATRIX_SIZE = 150  # 150x150 matrix

def matrix_worker(worker_id):
    start_time = time.time()
    loops = 0
    
    # Pre-generate matrices to avoid measuring generation time
    A = [[random.random() for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    B = [[random.random() for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
    
    print(f"[Worker {worker_id}] Started Matrix Mult (CPU Stress)")

    while time.time() - start_time < RUN_SECONDS:
        # Perform C = A * B
        C = [[0] * MATRIX_SIZE for _ in range(MATRIX_SIZE)]
        for i in range(MATRIX_SIZE):
            for j in range(MATRIX_SIZE):
                for k in range(MATRIX_SIZE):
                    C[i][j] += A[i][k] * B[k][j]
        loops += 1
    
    print(f"[Worker {worker_id}] DONE. Loops: {loops}")

if __name__ == "__main__":
    workers = os.cpu_count()
    print(f"Starting Matrix Stress on {workers} cores...")
    
    procs = []
    for i in range(workers):
        p = mp.Process(target=matrix_worker, args=(i,))
        p.start()
        procs.append(p)
    
    for p in procs:
        p.join()