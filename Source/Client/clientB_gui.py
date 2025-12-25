import socket
import threading

HOST = "0.0.0.0"
PORT = 7000


def start_client_b(log_callback=None):
    """
    Démarre le client B en écoute.
    log_callback : fonction pour envoyer les logs à la GUI
    """

    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    def serveur():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()

        log(f"Client B en écoute sur {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode()
            log(f"Message reçu de {addr} : {data}")
            conn.close()

    # Thread pour ne PAS bloquer l'interface
    threading.Thread(target=serveur, daemon=True).start()
