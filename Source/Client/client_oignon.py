import socket
import random

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000

def rsa_chiffrer(message, cle_publique):
    e, n = cle_publique
    return ",".join(str(pow(ord(c), e, n)) for c in message)

def demander_routeurs():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_CLIENT_PORT))

    buffer = ""
    while True:
        data = s.recv(1024).decode()
        if not data:
            break

        buffer += data
        if "END" in buffer:
            break

    s.close()

    routeurs = {}

    for ligne in buffer.split("\n"):
        ligne = ligne.strip()
        if not ligne or ligne == "END":
            continue

        try:
            r_id, ip, port, cle = ligne.split(";")
            e, n = cle.split(",")

            routeurs[r_id] = {
                "ip": ip,
                "port": int(port),
                "key": (int(e), int(n))
            }
        except ValueError:
            continue

    return routeurs


def choisir_chemin(routeurs, nb=3):
    ids = list(routeurs.keys())
    if len(ids) < nb:
        raise Exception(f"{len(ids)} routeur(s) disponible(s). {nb} requis.")
    return [(rid, routeurs[rid]) for rid in random.sample(ids, nb)]

def construire_oignon(chemin, message, dest_port):
    _, dernier = chemin[-1]
    message_chiffre = rsa_chiffrer(message, dernier["key"])

    payload = f"FINAL||{dest_port}||{message_chiffre}"

    for _, info in reversed(chemin):
        payload = f"{info['ip']}|{info['port']}||{payload}"

    return payload

def envoyer_message_oignon(message, dest_port):
    routeurs = demander_routeurs()
    chemin = choisir_chemin(routeurs)

    oignon = construire_oignon(chemin, message, dest_port)

    premier = chemin[0][1]
    s = socket.socket()
    s.connect((premier["ip"], premier["port"]))
    s.send(oignon.encode())
    s.close()

    return chemin
