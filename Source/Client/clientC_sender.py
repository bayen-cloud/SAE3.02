import socket
import random

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000
CLIENT_ID = "C"

# Destination finale : Client A
DEST_IP = "127.0.0.1"
DEST_PORT = 7001

# --------------------------------------------------
# Chiffrement RSA caractère par caractère
# --------------------------------------------------
def rsa_chiffrer(message, cle_publique):
    e, n = cle_publique
    blocs = []
    for c in message:
        blocs.append(str(pow(ord(c), e, n)))
    return ",".join(blocs)

# --------------------------------------------------
# Récupération des routeurs depuis le Master
# --------------------------------------------------
def demander_routeurs():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_CLIENT_PORT))
    data = s.recv(8192).decode()
    s.close()

    routeurs = {}
    for ligne in data.split("\n"):
        if ligne == "END":
            break

        r_id, ip, port, cle = ligne.split(";")
        e, n = cle.split(",")

        routeurs[r_id] = {
            "ip": ip,
            "port": int(port),
            "key": (int(e), int(n))
        }

    return routeurs

# --------------------------------------------------
# Construction de l'oignon
# --------------------------------------------------
def construire_oignon(chemin, message_final):
    # Chiffrement du message final avec la clé du dernier routeur
    dernier_id, dernier_info = chemin[-1]
    message_chiffre = rsa_chiffrer(message_final, dernier_info["key"])

    payload = f"FINAL||{message_chiffre}"

    # Ajout des couches de routage
    for _, info in reversed(chemin):
        route = f"{info['ip']}|{info['port']}"
        payload = f"{route}||{payload}"

    return payload

def choisir_chemin(routeurs):
    ids = list(routeurs.keys())
    chemin_ids = random.sample(ids, 3)
    return [(rid, routeurs[rid]) for rid in chemin_ids]

# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":

    print(f"\n=== CLIENT {CLIENT_ID} (EMETTEUR) ===")

    routeurs = demander_routeurs()
    chemin = choisir_chemin(routeurs)

    print("Chemin choisi :", [r[0] for r in chemin])

    message = "Bonjour depuis C"
    oignon = construire_oignon(chemin, message)

    print("Oignon construit et envoyé")

    premier = chemin[0][1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((premier["ip"], premier["port"]))
    s.send(oignon.encode())
    s.close()
