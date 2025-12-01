import socket
import random
import time

def register_to_master():
    master_ip = "127.0.0.1"   # Le master est sur ma machine (pour l'instant)
    master_port = 5000

    # Le routeur génère une fausse clé publique
    cle_publique = random.randint(1000, 9999)

    # Le routeur choisit un port où il va écouter
    port_d_ecoute = random.randint(6000, 7000)

    # Nom du routeur (pour le moment je mets R1)
    nom = "R1"

    # Message envoyé au master
    message = f"{nom}|{cle_publique}|{port_d_ecoute}"

    # Connexion au master
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((master_ip, master_port))
    print("Connecté au master...")

    print("Envoi des infos :", message)
    s.send(message.encode())

    s.close()

def main():
    print("Routeur R1 démarre...")
    register_to_master()
    print("Infos envoyées au master.")
    time.sleep(1)

main()