import socket
import threading
import mariadb   # module officiel MariaDB

# ------------------ CONFIG ------------------
HOST = "0.0.0.0"
PORT = 5000          # Port pour les ROUTEURS
CLIENT_PORT = 6000   # Port pour les CLIENTS

# Dictionnaire en mémoire
routeurs = {}

server_running = True


# ------------------------------------------------
# Connexion à la base MariaDB
# ------------------------------------------------
def connect_bdd():
    try:
        conn = mariadb.connect(
            host="127.0.0.1",
            port=3307,              # ton port MariaDB
            user="root",
            password="toto",        # ⚠ mets TON mot de passe
            database="sae302"
        )
        return conn
    except mariadb.Error as e:
        print(f"[MASTER] ERREUR MariaDB : {e}")
        exit(1)


# ------------------------------------------------
# Sauvegarde d’un routeur dans la base
# ------------------------------------------------
def save_routeur_bdd(router_id, ip, port_ecoute, cle_publique):
    conn = connect_bdd()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "REPLACE INTO routeurs (id, ip, port, cle_publique) VALUES (%s, %s, %s, %s)",
            (router_id, ip, port_ecoute, cle_publique)
        )

        conn.commit()
        print(f"[MASTER] Routeur {router_id} enregistré dans la base")

    except mariadb.Error as e:
        print(f"[MASTER] ERREUR SQL : {e}")

    cursor.close()
    conn.close()


# ------------------------------------------------
# Gestion connexion ROUTEUR
# ------------------------------------------------
def handle_router(conn, addr):
    print(f"[MASTER] Routeur connecté : {addr}")

    data = conn.recv(4096).decode()
    print(f"[MASTER] Reçu : {data}")

    try:
        router_id, cle_publique, port_ecoute = data.split("|")
        port_ecoute = int(port_ecoute)
    except:
        print("[MASTER] ERREUR format routeur")
        conn.close()
        return

    # Stockage mémoire
    routeurs[router_id] = {
        "ip": addr[0],
        "port": port_ecoute,
        "key": cle_publique
    }

    # Stockage base
    save_routeur_bdd(router_id, addr[0], port_ecoute, cle_publique)

    conn.send(f"OK routeur {router_id} enregistré".encode())
    conn.close()


# ------------------------------------------------
# Serveur ROUTEURS
# ------------------------------------------------
def server_loop(server):
    global server_running

    while server_running:
        try:
            server.settimeout(1)
            conn, addr = server.accept()
            threading.Thread(
                target=handle_router,
                args=(conn, addr),
                daemon=True
            ).start()
        except socket.timeout:
            continue


# ------------------------------------------------
# Gestion connexion CLIENT
# ------------------------------------------------
def handle_client(conn, addr):
    print(f"[MASTER] Client connecté : {addr}")

    message = ""
    for r_id, info in routeurs.items():
        message += f"{r_id};{info['ip']};{info['port']};{info['key']}\n"

    message += "END"

    conn.send(message.encode())
    conn.close()


# ------------------------------------------------
# Serveur CLIENTS
# ------------------------------------------------
def start_client_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, CLIENT_PORT))
    server.listen()

    print(f"[MASTER] Serveur client actif sur le port {CLIENT_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()


# ------------------------------------------------
# Démarrage du MASTER
# ------------------------------------------------
def start_master():
    global server_running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[MASTER] Démarré sur {HOST}:{PORT}")
    print("Tape 'list' pour afficher les routeurs")
    print("Tape 'stop' pour arrêter\n")

    #  Lancement du serveur CLIENT
    threading.Thread(
        target=start_client_server,
        daemon=True
    ).start()

    #  Lancement du serveur ROUTEUR
    server_thread = threading.Thread(
        target=server_loop,
        args=(server,),
        daemon=True
    )
    server_thread.start()

    # Console Master
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
                print(f"- {r} → {routeurs[r]}")
            print("================\n")

    print("[MASTER] Serveur arrêté proprement.")


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == "__main__":
    start_master()
