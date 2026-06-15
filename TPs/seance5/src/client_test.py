import socket
import json
import time

HOST = "192.168.56.1"   # IP DU MASTER
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connexion au MASTER...")

try:
    s.connect((HOST, PORT))
    print("Connecté au MASTER ✔")
except Exception as e:
    print("Erreur connexion MASTER :", e)
    exit()

for i in range(50):  # plus de messages pour voir backpressure
    msg = {
        "id": i,
        "timestamp": time.time()
    }

    try:
        s.send((json.dumps(msg) + "\n").encode())
        print("Envoyé :", i)
    except Exception as e:
        print("Erreur envoi :", e)
        break

    time.sleep(0.01)  # vitesse rapide → important pour backlog

s.close()
print("Client terminé")