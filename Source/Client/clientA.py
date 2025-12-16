import socket
import random

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000
CLIENT_ID = "A"

# -------- RSA CHIFFREMENT --------
def rsa_chiffrer(message, cle_publique):
    e, n = cle_publique
    m = int.from_bytes(message.encode(), "big")
    c = pow(m, e, n)
    return str(c)

# -------- MASTER --------
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

# -------- OIGNON --------
def construire_oignon(chemin, message_final):
    payload = f"FINAL|{message_final}"

    for _, info in reversed(chemin):
        couche = f"{info['ip']}|{info['port']}"
        rsa_couche = rsa_chiffrer(couche, info["key"])
        payload = f"{rsa_couche}|{payload}"

    return payload


def choisir_chemin(routeurs):
    ids = list(routeurs.keys())
    chemin_ids = random.sample(ids, 3)
    return [(rid, routeurs[rid]) for rid in chemin_ids]


if __name__ == "__main__":

    print(f"\n=== CLIENT {CLIENT_ID} (RSA PARTIEL) ===")

    routeurs = demander_routeurs()
    chemin = choisir_chemin(routeurs)

    print("Chemin choisi :", [r[0] for r in chemin])

    oignon = construire_oignon(chemin, f"HELLO_FROM_{CLIENT_ID}")
    print("\nOignon envoyé :", oignon)

    premier = chemin[0][1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((premier["ip"], premier["port"]))
    s.send(oignon.encode())
    s.close()
