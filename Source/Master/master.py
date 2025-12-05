import socket
import threading
import mariadb  # <-- IMPORTANT

HOST = "0.0.0.0"
PORT = 5000

routeurs = {}
server_running = True


# -------------------------------------------------------------------
# Connexion à MariaDB/MySQL
# -------------------------------------------------------------------
def connect_bdd():
    try:
        conn = mariadb.connect(
            host="127.0.0.1",
            user="root",
            password="TON_MOT_DE_PASSE",   # <-- Mets ton mot de passe ici
            database="sae302"
        )
        return conn

    except mariadb.Error as e:
        print(f"[MASTER] ERREUR MariaDB/MySQL : {e}")
        exit(1)


# -------------------------------------------------------------------
# Enregistrement du routeur dans la base
# -------------------------------------------------------------------
def save_routeur_bdd(router_id, ip, port_ecoute, cle_publique):
    conn = connect_bdd()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO routeurs (id, ip, port, cle_publique) VALUES (%s, %s, %s, %s)",
            (router_id, ip, port_ecoute, cle_publique)
        )
        conn.commit()
        print(f"[MASTER] Routeur {router_id} enregistré dans la base.")

    except mariadb.Error as e:
        print(f"[MASTER] ERREUR SQL : {e}")

    cursor.close()
    conn.close()


# -------------------------------------------------------------------
# Gestion de la connexion d’un routeur
# -------------------------------------------------------------------
def handle_router(conn, addr):
    print(f"[MASTER] Nouveau routeur connecté : {addr}")

    data = conn.recv(4096).decode()
    print(f"[MASTER] Reçu : {data}")

    try:
        router_id, cle_publique, port_ecoute = data.split("|")
        port_ecoute = int(port_ecoute)
    except:
        print("[MASTER] ERREUR format")
        conn.close()
        return

    routeurs[router_id] = {
        "ip": addr[0],
        "key": cle_publique,
        "port": port_ecoute
    }

    save_routeur_bdd(router_id, addr[0], port_ecoute, cle_publique)

    conn.send(f"OK routeur {router_id} enregistré".encode())
    conn.close()


# -------------------------------------------------------------------
# Boucle serveur
# -------------------------------------------------------------------
def server_loop(server):
    global server_running

    while server_running:
        try:
            server.settimeout(1)
            conn, addr = server.accept()
            threading.Thread(target=handle_router, args=(conn, addr)).start()
        except socket.timeout:
            continue


# -------------------------------------------------------------------
# Lancement du Master
# -------------------------------------------------------------------
def start_master():
    global server_running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[MASTER] Démarré sur {HOST}:{PORT}")
    print("Tape 'stop' pour arrêter.")
    print("Tape 'list' pour afficher les routeurs.\n")

    server_thread = threading.Thread(target=server_loop, args=(server,))
    server_thread.start()

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "stop":
            print("[MASTER] Arrêt du serveur...")
            server_running = False
            server.close()
            break

        elif cmd == "list":
            print("\n=== ROUTEURS ===")
            for r in routeurs:
                print(f"- {r} : {routeurs[r]}")
            print("================\n")

    print("[MASTER] Serveur arrêté proprement.")


if __name__ == "__main__":
    start_master()

