import socket
import sys
import threading
import random
import math
from sympy import isprime

# =====================================================
# PARAMÈTRES DU ROUTEUR (arguments ligne de commande)
# =====================================================
ROUTER_ID = sys.argv[1]          # Exemple : R1
LISTEN_PORT = int(sys.argv[2])  # Exemple : 1800

HOST = "0.0.0.0"
MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

CLIENT_B_IP = "127.0.0.1"
CLIENT_B_PORT = 7000

# =====================================================
# RSA PÉDAGOGIQUE (caractère par caractère)
# =====================================================

def generer_nombre_premier():
    """Génère un nombre premier."""
    while True:
        n = random.randint(1000, 5000)
        if isprime(n):
            return n


def generer_cle_rsa():
    """Génère une paire de clés RSA."""
    p = generer_nombre_premier()
    q = generer_nombre_premier()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3

    d = pow(e, -1, phi)
    return (e, n), (d, n)


def rsa_dechiffrer(message_chiffre, cle_privee):
    """
    Déchiffre un message RSA caractère par caractère.
    Format attendu : "c1,c2,c3,..."
    """
    d, n = cle_privee
    message = ""

    blocs = message_chiffre.split(",")

    for bloc in blocs:
        m = pow(int(bloc), d, n)
        message += chr(m)

    return message


# Génération des clés au démarrage
CLE_PUBLIQUE, CLE_PRIVEE = generer_cle_rsa()

# =====================================================
# ENREGISTREMENT AUPRÈS DU MASTER
# =====================================================

def enregistrer_au_master():
    """Enregistre le routeur auprès du Master."""
    e, n = CLE_PUBLIQUE
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))
        s.send(f"{ROUTER_ID}|{e},{n}|{LISTEN_PORT}".encode())
        print(f"[{ROUTER_ID}] {s.recv(1024).decode()}")
        s.close()
    except Exception as e:
        print(f"[{ROUTER_ID}] Erreur Master : {e}")

# =====================================================
# TRAITEMENT DES MESSAGES (ROUTAGE EN OIGNON)
# =====================================================

def handle_message(conn, addr):
    try:
        data = conn.recv(8192).decode()
        print(f"[{ROUTER_ID}] Reçu : {data}")

        route, payload = data.split("||", 1)

        # =========================
        # CAS FINAL : ENVOI AU CLIENT
        # =========================
        if route == "FINAL":
            dest_port_str, message_chiffre = payload.split("||", 1)
            dest_port = int(dest_port_str)

            # Déchiffrement
            message = rsa_dechiffrer(message_chiffre, CLE_PRIVEE)

            print(f"[{ROUTER_ID}] Message final déchiffré : {message}")
            print(f"[{ROUTER_ID}] Envoi vers client sur port {dest_port}")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", dest_port))
            s.send(message.encode())
            s.close()
            return

        # =========================
        # ROUTAGE NORMAL
        # =========================
        next_ip, next_port = route.split("|")
        next_port = int(next_port)

        print(f"[{ROUTER_ID}] → Prochain saut {next_ip}:{next_port}")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((next_ip, next_port))
        s.send(payload.encode())
        s.close()

    except Exception as e:
        print(f"[{ROUTER_ID}] Erreur traitement message : {e}")


# =====================================================
# SERVEUR DU ROUTEUR
# =====================================================

def start_router():
    """Démarre le serveur TCP du routeur."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, LISTEN_PORT))
    server.listen()

    print(f"[{ROUTER_ID}] Routeur actif sur le port {LISTEN_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_message,
            args=(conn, addr),
            daemon=True
        ).start()

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    enregistrer_au_master()
    start_router()
