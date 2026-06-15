import queue, threading, time, random, uuid

class Metrics:
    def __init__(self):
        self.processed = 0
        self.total_latency = 0.0
        self._lock = threading.Lock()

    def record(self, latency: float):
        with self._lock:
            self.processed += 1
            self.total_latency += latency

    def snapshot(self):
        with self._lock:
            avg_lat = (self.total_latency / self.processed) if self.processed else 0
            return {"processed": self.processed, "avg_latency_ms": round(avg_lat * 1000, 1)}

def monitored_worker(q, metrics, stop):
    while not stop.is_set():
        try:
            msg = q.get(timeout=1)
        except queue.Empty:
            continue
        time.sleep(random.uniform(0.05, 0.2))  # traitement
        latency = time.time() - msg["created_at"]
        metrics.record(latency)
        q.task_done()

def monitor(q, metrics, stop, interval=2):
    while not stop.is_set():
        snap = metrics.snapshot()
        print(f"[Monitor] backlog={q.qsize():>4}  processed={snap['processed']:>4}  "
              f"avg_latency={snap['avg_latency_ms']:>6.1f}ms")
        time.sleep(interval)

# Utilisation : lancer producer, 2 workers, 1 monitor en threads séparés.