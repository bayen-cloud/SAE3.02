import socket
import random

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000
CLIENT_ID = "A"

# =====================================================
# RSA CHIFFREMENT (caractère par caractère)
# =====================================================
def rsa_chiffrer(message, cle_publique):
    """
    Chiffre un message caractère par caractère avec RSA
    Retourne une chaîne "c1,c2,c3,..."
    """
    e, n = cle_publique
    blocs = []

    for caractere in message:
        m = ord(caractere)
        c = pow(m, e, n)
        blocs.append(str(c))

    return ",".join(blocs)

# =====================================================
# RÉCUPÉRATION DES ROUTEURS DEPUIS LE MASTER
# =====================================================
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
            # Ligne incomplète ignorée
            continue

    return routeurs



# =====================================================
# CONSTRUCTION DE L’OIGNON
# =====================================================
def construire_oignon(chemin, message_final):
    """
    Construit le message en oignon
    """
    _, dernier = chemin[-1]

    message_chiffre = rsa_chiffrer(message_final, dernier["key"])
    payload = f"FINAL||{message_chiffre}"

    for _, info in reversed(chemin):
        route = f"{info['ip']}|{info['port']}"
        payload = f"{route}||{payload}"

    return payload

def choisir_chemin(routeurs):
    ids = list(routeurs.keys())

    if len(ids) < 3:
        raise Exception(
            f"Erreur : {len(ids)} routeur(s) disponible(s). "
            "Au moins 3 routeurs sont nécessaires."
        )

    chemin_ids = random.sample(ids, 3)
    return [(rid, routeurs[rid]) for rid in chemin_ids]

# =====================================================
# FONCTION UTILISABLE PAR L’INTERFACE GRAPHIQUE
# =====================================================
def envoyer_message(message):
    routeurs = demander_routeurs()
    chemin = choisir_chemin(routeurs)

    print("Chemin choisi :", [rid for rid, _ in chemin])

    oignon = construire_oignon(chemin, message)

    print("Oignon envoyé :", oignon)

    premier = chemin[0][1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((premier["ip"], premier["port"]))
    s.send(oignon.encode())
    s.close()

# =====================================================
# MAIN (mode console, pour tests)
# =====================================================
if __name__ == "__main__":
    print(f"\n=== CLIENT {CLIENT_ID} ===")
    envoyer_message("Bonjour")
