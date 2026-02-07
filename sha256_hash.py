# SHA-256 hashing stress test to stress CPU
import multiprocessing as mp
import os
import time
import hashlib

RUN_SECONDS = 60

def hash_worker(worker_id):
    start_time = time.time()
    hashes = 0
    data = b"InitialBlockDataForStressTest"
    
    print(f"[Worker {worker_id}] Started Hashing (Crypto Stress)")

    while time.time() - start_time < RUN_SECONDS:
        # repeatedly hash the previous hash
        # This keeps the CPU pinned without waiting for memory
        for _ in range(10000):
            data = hashlib.sha256(data).digest()
        hashes += 10000

    print(f"[Worker {worker_id}] DONE. MH/s: {hashes / RUN_SECONDS / 1_000_000:.2f}")

if __name__ == "__main__":
    workers = os.cpu_count()
    print(f"Starting SHA-256 Stress on {workers} cores...")
    
    procs = []
    for i in range(workers):
        p = mp.Process(target=hash_worker, args=(i,))
        p.start()
        procs.append(p)
    
    for p in procs:
        p.join()