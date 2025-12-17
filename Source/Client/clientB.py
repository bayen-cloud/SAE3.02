import socket
import threading

# Adresse d'écoute du client B
HOST = "0.0.0.0"
PORT = 7000   # Port du client B (tu peux garder 7000)

def handle_conn(conn, addr):
    """Traite un message reçu."""
    try:
        data = conn.recv(8192).decode()
        print(f"[Client B] Message reçu de {addr} : {data}")
    except Exception as e:
        print(f"[Client B] Erreur réception : {e}")
    finally:
        conn.close()

def start_client_b():
    """Démarre le serveur TCP du client B."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[Client B] En écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_conn, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_client_b()
