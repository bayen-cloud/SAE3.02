import socket
import threading

HOST = "0.0.0.0"
PORT = 7000

def start_client_b(log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    def serveur():
        s = socket.socket()
        s.bind((HOST, PORT))
        s.listen()
        log(f"Client B en écoute sur {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode()
            conn.close()
            log(f"Message reçu de {addr[0]}:{addr[1]} : {data}")

    threading.Thread(target=serveur, daemon=True).start()
