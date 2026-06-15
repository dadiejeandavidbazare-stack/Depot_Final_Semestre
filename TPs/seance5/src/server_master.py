import socket
import threading
import json
import queue
import time

HOST = "0.0.0.0"
PORT = 5000

WORKER_PORT = 5001
worker_conn = None

main_queue = queue.Queue()

# =========================
# CLIENT HANDLER
# =========================
def handle_client(conn):
    buffer = ""

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                msg_str, buffer = buffer.split("\n", 1)
                msg = json.loads(msg_str)

                main_queue.put(msg)

                print(f"[MASTER] Message reçu → {msg}")

                # envoyer au worker si connecté
                if worker_conn:
                    try:
                        worker_conn.send((json.dumps(msg) + "\n").encode())
                    except:
                        pass

        except:
            break

    conn.close()


# =========================
# MONITOR QUEUE
# =========================
def monitor_queue():
    while True:
        print(f"[MASTER] Taille queue = {main_queue.qsize()}")
        time.sleep(1)


# =========================
# WORKER HANDLER
# =========================
def handle_worker(conn):
    global worker_conn
    worker_conn = conn
    print("🔵 Worker connecté ✔")


# =========================
# WORKER SERVER (port 5001)
# =========================
def start_worker_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", WORKER_PORT))
    s.listen()

    print("🚀 Worker server lancé sur port 5001")

    while True:
        conn, addr = s.accept()
        print(f"🔵 Worker connecté depuis {addr}")
        threading.Thread(target=handle_worker, args=(conn,), daemon=True).start()


# =========================
# MAIN SERVER
# =========================
def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print("✅ MASTER lancé sur port 5000")
    print("En attente de connexions...")

    # monitor queue
    threading.Thread(target=monitor_queue, daemon=True).start()

    # worker server
    threading.Thread(target=start_worker_server, daemon=True).start()

    while True:
        conn, addr = s.accept()
        print(f"🔗 Client connecté depuis {addr}")

        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    start_server()