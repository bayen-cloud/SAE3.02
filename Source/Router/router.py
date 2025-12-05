import socket
import threading
import random
import sys

# Adresse du Master
MASTER_IP = "127.0.0.1"
MASTER_PORT = 5000

# -------------------------------------------------------------------
# Fonction pour générer une fausse clé publique (temporaire)
# Plus tard on remplacera par de la vraie cryptographie RSA maison
# -------------------------------------------------------------------
def generate_fake_public_key():
    # Création d'une clé fictive de 64 chiffres
    return "".join([str(random.randint(0,9)) for _ in range(64)])


# -------------------------------------------------------------------
# Serveur interne du routeur :
# Ce serveur écoute sur un port donné et attend les messages
# venant d'autres routeurs dans la chaîne (routage en oignon).
# -------------------------------------------------------------------
def router_server(port, router_id):

    # Création d'un socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # On attache le serveur à l'adresse locale 0.0.0.0 (toutes interfaces)
    server.bind(("0.0.0.0", port))

    # Le routeur se met en mode écoute (listen)
    server.listen()

    print(f"[{router_id}] Routeur en écoute sur le port {port}")

    # Boucle infinie : le routeur attend toujours des messages entrants
    while True:

        # Acceptation d'une nouvelle connexion entrante
        conn, addr = server.accept()

        print(f"[{router_id}] Message reçu depuis {addr}")

        # Réception des données (max 4096 octets)
        data = conn.recv(4096).decode()

        print(f"[{router_id}] Contenu reçu : {data}")

        # Fermeture de la connexion courte
        conn.close()


# -------------------------------------------------------------------
# Fonction pour se connecter au Master :
# Le routeur envoie son ID, sa clé publique, et son port d'écoute.
# -------------------------------------------------------------------
def connect_to_master(router_id, port_listen):

    # Génération d'une fausse clé publique
    cle_publique = generate_fake_public_key()

    # Format imposé pour que le Master puisse extraire les infos
    message = f"{router_id}|{cle_publique}|{port_listen}"

    # Création du socket client TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connexion au Master
        s.connect((MASTER_IP, MASTER_PORT))
        print(f"[{router_id}] Connecté au Master")

        # Envoi de nos informations au Master
        s.send(message.encode())
        print(f"[{router_id}] Clé + port envoyés au Master")

        # Réception de la réponse du Master
        response = s.recv(4096).decode()
        print(f"[{router_id}] Réponse du Master : {response}")

    except Exception as e:
        print(f"[{router_id}] Erreur connexion Master :", e)

    # Fermeture du socket
    s.close()


# -------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------
if __name__ == "__main__":

    # On vérifie que l'utilisateur donne bien deux arguments :
    #  - ID du routeur
    #  - Port d'écoute
    if len(sys.argv) != 3:
        print("Utilisation : python3 router.py <ID_ROUTEUR> <PORT_ECOUTE>")
        sys.exit(1)

    router_id = sys.argv[1]
    port_listen = int(sys.argv[2])

    # Lancement du serveur du routeur dans un thread séparé
    # pour pouvoir écouter ET parler au Master en même temps.
    server_thread = threading.Thread(
        target=router_server,
        args=(port_listen, router_id),
        daemon=True  # daemon=True → arrêt quand le programme principal s'arrête
    )
    server_thread.start()

    # Connexion au Master
    connect_to_master(router_id, port_listen)

    # Boucle vide pour que le programme reste actif
    while True:
        pass
