import socket
import threading

# Client C écoute sur un port dédié
HOST = "0.0.0.0"
PORT = 7002  # Port du client C

def handle_conn(conn, addr):
    """Affiche le message reçu puis ferme la connexion."""
    try:
        data = conn.recv(8192).decode()
        print(f"[Client C] Message reçu de {addr} : {data}")
    except Exception as e:
        print(f"[Client C] Erreur réception : {e}")
    finally:
        conn.close()

def start_client_c():
    """Démarre le serveur TCP du client C."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[Client C] En écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_conn, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_client_c()
