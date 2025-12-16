import socket
import sys
import threading
import random
import math
import time
from sympy import isprime

# =====================================================
# PARAMÈTRES DU ROUTEUR (passés en argument)
# =====================================================
ROUTER_ID = sys.argv[1]          # ex: R1
LISTEN_PORT = int(sys.argv[2])  # ex: 1800

HOST = "0.0.0.0"
MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

# =====================================================
# RSA "MAISON" (PÉDAGOGIQUE)
# =====================================================

def generer_nombre_premier():
    """Génère un nombre premier suffisamment grand"""
    while True:
        n = random.randint(1000, 5000)
        if isprime(n):
            return n


def generer_cle_rsa():
    """Génère une paire de clés RSA (publique, privée)"""
    p = generer_nombre_premier()
    q = generer_nombre_premier()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3

    d = pow(e, -1, phi)
    return (e, n), (d, n)


def rsa_dechiffrer(chiffre, cle_privee):
    """Déchiffre un entier RSA et retourne une chaîne"""
    d, n = cle_privee
    c = int(chiffre)
    m = pow(c, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, "big").decode()


# Génération des clés RSA AU DÉMARRAGE
CLE_PUBLIQUE, CLE_PRIVEE = generer_cle_rsa()

# =====================================================
# ENREGISTREMENT AUPRÈS DU MASTER
# =====================================================

def enregistrer_au_master():
    """Envoie l'identité et la clé publique au Master"""
    e, n = CLE_PUBLIQUE
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))
        s.send(f"{ROUTER_ID}|{e},{n}|{LISTEN_PORT}".encode())
        print(f"[{ROUTER_ID}] {s.recv(1024).decode()}")
        s.close()
    except Exception as err:
        print(f"[{ROUTER_ID}] ❌ Erreur Master : {err}")

# =====================================================
# TRAITEMENT DES MESSAGES (ROUTAGE EN OIGNON)
# =====================================================

def handle_message(conn, addr):
    """Traite un message entrant (une couche d'oignon)"""
    data = conn.recv(8192).decode()
    print(f"[{ROUTER_ID}] Reçu : {data}")

    # Séparation de la couche RSA et du reste
    try:
        rsa_part, reste = data.split("|", 1)
        clair = rsa_dechiffrer(rsa_part, CLE_PRIVEE)
    except Exception as e:
        print(f"[{ROUTER_ID}] ❌ Erreur déchiffrement : {e}")
        conn.close()
        return

    # Si c'est la dernière couche
    if clair == "FINAL":
        print(f"[{ROUTER_ID}] 🎉 MESSAGE FINAL : {reste}")
        conn.close()
        return

    # Sinon, on récupère le prochain saut
    try:
        next_ip, next_port = clair.split("|")
        next_port = int(next_port)
    except:
        print(f"[{ROUTER_ID}] ❌ Format IP|PORT invalide : {clair}")
        conn.close()
        return

    print(f"[{ROUTER_ID}] → Prochain saut {next_ip}:{next_port}")

    # Envoi au routeur suivant (avec retry)
    for tentative in range(3):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((next_ip, next_port))
            s.send(reste.encode())
            s.close()
            print(f"[{ROUTER_ID}] Message transmis")
            break
        except Exception as e:
            print(f"[{ROUTER_ID}] Tentative {tentative+1} échouée")
            time.sleep(0.5)
    else:
        print(f"[{ROUTER_ID}] ❌ Impossible de joindre {next_ip}:{next_port}")

    conn.close()

# =====================================================
# SERVEUR DU ROUTEUR
# =====================================================

def start_router():
    """Lance le serveur TCP du routeur"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, LISTEN_PORT))
    server.listen()

    print(f"[{ROUTER_ID}] Routeur RSA actif sur {LISTEN_PORT}")

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
