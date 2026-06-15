import queue, threading, time, random, uuid, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s")

def demo_producer(q, n=10):
    for i in range(n):
        msg = {"id": str(uuid.uuid4())[:8], "value": round(random.uniform(10, 40), 1)}
        q.put(msg)
        logging.info(f"Produit: {msg['id']} val={msg['value']}")
        time.sleep(random.uniform(0.05, 0.15))

def demo_worker(q, stop):
    while not stop.is_set():
        try:
            msg = q.get(timeout=1)
            time.sleep(0.1)  # simule traitement
            logging.info(f"Traité: {msg['id']} val={msg['value']}")
            q.task_done()
        except queue.Empty:
            continue

if __name__ == "__main__":
    q = queue.Queue(maxsize=5)
    stop = threading.Event()
    t_prod = threading.Thread(target=demo_producer, args=(q,), name="Producer")
    t_work = threading.Thread(target=demo_worker, args=(q, stop), name="Worker-1")
    t_work.start(); t_prod.start()
    t_prod.join()
    q.join()       # attend que tous les messages soient traités
    stop.set()
    t_work.join()
    logging.info("Pipeline terminé.")