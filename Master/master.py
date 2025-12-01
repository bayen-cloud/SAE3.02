import socket
import threading

# Fonction qui gère la connexion d'un routeur
def handle_router(conn, addr):
    print("Routeur connecté :", addr)

    # Le routeur envoie ses infos : nom | clé publique | port
    data = conn.recv(1024).decode()
    print("Infos reçues :", data)

    conn.close()

# Fonction principale du Master
def start_master():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind(("0.0.0.0", 5000))   # Le master écoute sur le port 5000
    serveur.listen(5)

    print("Master prêt. En écoute sur le port 5000...")

    while True:
        conn, addr = serveur.accept()

        # On lance un thread pour gérer chaque routeur
        thread = threading.Thread(target=handle_router, args=(conn, addr))
        thread.start()

start_master()