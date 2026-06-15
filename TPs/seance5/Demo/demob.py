import queue, threading, time, random, uuid, logging
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s")

@dataclass
class Msg:
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    value: float = 0.0
    attempts: int = 0

def retry_worker(main_q, dlq, stop):
    while not stop.is_set():
        try:
            msg = main_q.get(timeout=1)
        except queue.Empty:
            continue
        msg.attempts += 1
        # Simule un échec 30 % du temps
        if random.random() < 0.3:
            if msg.attempts >= 3:
                dlq.put(msg)
                logging.warning(f"DLQ: {msg.msg_id} après {msg.attempts} tentatives")
            else:
                main_q.put(msg)  # retry
                logging.info(f"Retry #{msg.attempts}: {msg.msg_id}")
        else:
            logging.info(f"OK: {msg.msg_id} (tentative {msg.attempts})")
        main_q.task_done()

if __name__ == "__main__":
    main_q = queue.Queue(maxsize=20)
    dlq = queue.Queue()
    stop = threading.Event()
    # Produit 15 messages
    for _ in range(15):
        main_q.put(Msg(value=round(random.uniform(10, 40), 1)))
    w = threading.Thread(target=retry_worker, args=(main_q, dlq, stop), name="Worker")
    w.start()
    time.sleep(5)
    stop.set(); w.join()
    logging.info(f"Dead-letter: {dlq.qsize()} messages")