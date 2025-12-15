import socket
import random

# ------------------------------------------------
# CONFIGURATION
# ------------------------------------------------
MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000

CLIENT_ID = "A"   # Identifiant du client


# ------------------------------------------------
# Demande de la liste des routeurs au Master
# ------------------------------------------------
def demander_routeurs():
    """
    Le client se connecte au Master pour récupérer
    la liste des routeurs disponibles.

    Format reçu :
    R1;IP;PORT;CLE
    R2;IP;PORT;CLE
    ...
    END
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_CLIENT_PORT))

    data = s.recv(4096).decode()
    s.close()

    routeurs = {}
    lignes = data.split("\n")

    for ligne in lignes:
        if ligne == "END":
            break

        r_id, ip, port, cle = ligne.split(";")

        routeurs[r_id] = {
            "ip": ip,
            "port": int(port),
            "key": cle
        }

    return routeurs


# ------------------------------------------------
# Choix aléatoire de 3 routeurs
# ------------------------------------------------
def choisir_chemin(routeurs):
    """
    Sélectionne aléatoirement 3 routeurs
    parmi ceux fournis par le Master.
    """

    ids = list(routeurs.keys())
    chemin_ids = random.sample(ids, 3)

    chemin = []
    for r_id in chemin_ids:
        chemin.append((r_id, routeurs[r_id]))

    return chemin


# ------------------------------------------------
# Construction du message en couches (oignon)
# ------------------------------------------------
def construire_oignon(chemin, message_final):
    """
    Construit un message en couches successives.
    Chaque couche contient l'adresse du prochain routeur.
    """

    # Couche la plus interne (message final)
    payload = f"FINAL|{message_final}"

    # Ajout des couches en partant du dernier routeur
    for r_id, info in reversed(chemin):
        payload = f"{info['ip']}|{info['port']}|{payload}"

    return payload


# ------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------
if __name__ == "__main__":

    print(f"\n=== CLIENT {CLIENT_ID} ===")

    # 1) Récupération des routeurs depuis le Master
    routeurs = demander_routeurs()

    print("\nRouteurs disponibles :")
    for r in routeurs:
        print(f"- {r} ({routeurs[r]['ip']}:{routeurs[r]['port']})")

    # 2) Choix du chemin anonymisé
    chemin = choisir_chemin(routeurs)

    print("\nChemin anonymisé choisi :")
    for i, (r_id, info) in enumerate(chemin, start=1):
        print(f"  Saut {i} → {r_id} ({info['ip']}:{info['port']})")

    # 3) Message final
    message_final = "HELLO_FROM_CLIENT_" + CLIENT_ID

    # 4) Construction de l'oignon
    oignon = construire_oignon(chemin, message_final)

    print("\nMessage en couches (oignon) construit :\n")
    print(oignon)

    # 5) Envoi de l'oignon au premier routeur
    premier_routeur = chemin[0][1]  # info du premier saut

    print("\nEnvoi du message au premier routeur...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((premier_routeur["ip"], premier_routeur["port"]))
    s.send(oignon.encode())
    s.close()

    print("Message envoyé.")
