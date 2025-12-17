import socket
import threading

HOST = "0.0.0.0"
PORT = 7001   # Port d'écoute du Client A

def handle_conn(conn, addr):
    try:
        data = conn.recv(8192).decode()
        print(f"[Client A] Message reçu de {addr} : {data}")
    except Exception as e:
        print(f"[Client A] Erreur réception : {e}")
    finally:
        conn.close()

def start_client_a():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[Client A] En écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_conn,
            args=(conn, addr),
            daemon=True
        ).start()

if __name__ == "__main__":
    start_client_a()
