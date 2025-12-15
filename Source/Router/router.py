import socket
import sys
import threading
import random

# ------------------------------------------------
# ARGUMENTS
# ------------------------------------------------
ROUTER_ID = sys.argv[1]
LISTEN_PORT = int(sys.argv[2])

HOST = "0.0.0.0"
MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000


# ------------------------------------------------
# Génération d'une clé publique simple (maison)
# ------------------------------------------------
def generer_cle_publique():
    # Clé symbolique pour l'instant (RSA plus tard)
    return str(random.getrandbits(128))


# ------------------------------------------------
# Enregistrement auprès du Master
# ------------------------------------------------
def enregistrer_au_master():
    cle_publique = generer_cle_publique()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))

        message = f"{ROUTER_ID}|{cle_publique}|{LISTEN_PORT}"
        s.send(message.encode())

        reponse = s.recv(1024).decode()
        print(f"[{ROUTER_ID}] Réponse du Master : {reponse}")

        s.close()
    except Exception as e:
        print(f"[{ROUTER_ID}] ❌ Impossible de contacter le Master : {e}")


# ------------------------------------------------
# Gestion d'un message reçu (oignon)
# ------------------------------------------------
def handle_message(conn, addr):
    print(f"[{ROUTER_ID}] Message reçu de {addr}")

    data = conn.recv(4096).decode()
    print(f"[{ROUTER_ID}] Données : {data}")

    parts = data.split("|", 2)

    # Cas FINAL
    if parts[0] == "FINAL":
        print(f"[{ROUTER_ID}] 🎉 MESSAGE FINAL REÇU : {parts[1]}")
        conn.close()
        return

    # Cas intermédiaire
    try:
        next_ip = parts[0]
        next_port = int(parts[1])
        payload = parts[2]
    except:
        print(f"[{ROUTER_ID}] ❌ Format invalide")
        conn.close()
        return

    print(f"[{ROUTER_ID}] → Prochain saut : {next_ip}:{next_port}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((next_ip, next_port))
        s.send(payload.encode())
        s.close()
        print(f"[{ROUTER_ID}] Message transmis")
    except Exception as e:
        print(f"[{ROUTER_ID}] ❌ Erreur transmission : {e}")

    conn.close()


# ------------------------------------------------
# Serveur du routeur
# ------------------------------------------------
def start_router():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, LISTEN_PORT))
    server.listen()

    print(f"[{ROUTER_ID}] Routeur en écoute sur le port {LISTEN_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_message,
            args=(conn, addr),
            daemon=True
        ).start()


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == "__main__":
    # 1) Enregistrement auprès du Master
    enregistrer_au_master()

    # 2) Démarrage du routeur
    start_router()
