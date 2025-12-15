import socket
import random

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000

CLIENT_ID = "C"   # A, B ou C


def demander_routeurs():
    """
    Demande au Master la liste des routeurs disponibles.
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


def choisir_chemin(routeurs):
    """
    Choisit aléatoirement 3 routeurs parmi ceux disponibles.
    """
    ids = list(routeurs.keys())
    chemin_ids = random.sample(ids, 3)

    chemin = []
    for r_id in chemin_ids:
        chemin.append((r_id, routeurs[r_id]))

    return chemin


if __name__ == "__main__":

    print(f"\n=== CLIENT {CLIENT_ID} ===")

    # 1) Récupération des routeurs
    routeurs = demander_routeurs()

    print("Routeurs disponibles :")
    for r in routeurs:
        print(f"- {r} ({routeurs[r]['ip']}:{routeurs[r]['port']})")

    # 2) Choix du chemin
    chemin = choisir_chemin(routeurs)

    print("\nChemin anonymisé choisi :")
    for i, (r_id, info) in enumerate(chemin, start=1):
        print(f"  Saut {i} → {r_id} ({info['ip']}:{info['port']})")
