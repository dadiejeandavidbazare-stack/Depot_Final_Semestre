import os
import json
from client import RpcClient

def run_scenario():
    print("=" * 50)
    print("TEST 1 : health.ping")
    
    # Initialisation du client (ajuste l'URL si ton serveur tourne sur un autre port)
    client = RpcClient("http://127.0.0.1:8080")
    
    # Exécution du ping
    ping_reply = client.call("health.ping")
    if ping_reply.get("result") and ping_reply["result"].get("status") == "ok":
        print("  ✅ Ping OK")
    else:
        print("  ❌ Échec du Ping:", ping_reply)
        return

    print("\n" + "=" * 50)
    print("TEST 2 : ingest.batch")
    
    # ── RÉSOLUTION DYNAMIQUE DU CHEMIN (Anti-FileNotFoundError) ──
    # Récupère le dossier où se trouve physiquement ce script test_scenario.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construit le chemin absolu vers 'test_batch.json' dans ce même dossier
    json_path = os.path.join(script_dir, "test_batch.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            batch_data = json.load(f)
    except FileNotFoundError:
        print(f"  ❌ Erreur critique : Le fichier '{json_path}' est introuvable.")
        print("     Assure-toi que 'test_batch.json' est bien dans le même dossier que ce script.")
        return

    # Envoi du batch au serveur RPC
    # On passe le contenu du fichier dans le paramètre 'readings' requis par ingest_batch
    ingest_reply = client.call("ingest.batch", {"readings": batch_data})
    
    if ingest_reply.get("error"):
        print("  ❌ Le serveur a retourné une erreur protocolaire :")
        print(f"     Code {ingest_reply['error']['code']} : {ingest_reply['error']['message']}")
    else:
        result = ingest_reply.get("result", {})
        print("  ✅ Ingestion terminée avec succès !")
        print(f"     ├─ Enregistrements acceptés : {result.get('accepted', 0)}")
        print(f"     └─ Enregistrements rejetés : {result.get('rejected', 0)}")
        if result.get("rejected", 0) > 0:
            print("     ⚠️ Détails des anomalies reçues :")
            for err in result.get("errors", []):
                print(f"        - Index {err.get('index')}: {err.get('errors')}")

if __name__ == "__main__":
    run_scenario()