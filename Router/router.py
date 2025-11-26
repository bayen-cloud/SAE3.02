import socket
import threading

from crypto import generate_keys, decrypt

MASTER_IP = "192.168.56.4"  # IP de ta VM master
MASTER_PORT = 5000

ROUTER_NAME = "R1"
ROUTER_PORT = 6001  # port du routeur

# ----------------------------------------------------
# Envoi d’informations au master
# ----------------------------------------------------

def register_to_master(public_key):
    e, n = public_key
    message = (
        "TYPE:ROUTER\n"
        f"NAME:{ROUTER_NAME}\n"
        f"PORT:{ROUTER_PORT}\n"
        f"PUBLIC_KEY:{e};{n}\n"
        "END\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((MASTER_IP, MASTER_PORT))
    sock.send(message.encode())
    sock.close()

    print("[ROUTEUR] Enregistré auprès du master.")

# ----------------------------------------------------
# Serveur socket du routeur
# ----------------------------------------------------

def handle_client(conn, private_key):
    try:
        data = conn.recv(4096).decode()
        if not data:
            return

        # Déchiffrement RSA
        message = decrypt(data, private_key)

        # Format attendu : next_ip|next_port|payload
        parts = message.split("|", 2)

        if len(parts) != 3:
            print("[ROUTEUR] Message incomplet.")
            return

        next_ip, next_port, payload = parts
        next_port = int(next_port)

        print(f"[ROUTEUR] Reçu → envoi à {next_ip}:{next_port}")

        # Forward vers le prochain routeur
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward_socket.connect((next_ip, next_port))
        forward_socket.send(payload.encode())
        forward_socket.close()

    except Exception as e:
        print("[ROUTEUR] Erreur handle_client :", e)

    finally:
        conn.close()

def start_router_server(private_key):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", ROUTER_PORT))
    sock.listen(5)

    print(f"[ROUTEUR] En écoute sur le port {ROUTER_PORT}...")

    while True:
        conn, addr = sock.accept()
        print("[ROUTEUR] Connexion de :", addr)
        threading.Thread(target=handle_client, args=(conn, private_key)).start()

# ----------------------------------------------------
# MAIN
# ----------------------------------------------------

if __name__ == "__main__":

    # Génération des clés RSA
    public_key, private_key = generate_keys()

    print("[ROUTEUR] Clé publique :", public_key)
    print("[ROUTEUR] Clé privée :", private_key)

    # Envoi au master
    register_to_master(public_key)

    # Lancement du serveur socket
    start_router_server(private_key)
