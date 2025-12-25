import socket
import threading
import mariadb
import time

HOST = "0.0.0.0"
ROUTER_PORT = 5000
CLIENT_PORT = 6000

routeurs = {}
routeurs_lock = threading.Lock()
server_running = True

# =====================================================
# CONNEXION BASE DE DONNÉES
# =====================================================
def connect_bdd():
    return mariadb.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="toto",
        database="sae302"
    )

# =====================================================
# LOG (injecté par la GUI)
# =====================================================
def log(message, callback=None):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    if callback:
        callback(line)
    else:
        print(line)

# =====================================================
# ROUTEURS
# =====================================================
def handle_router(conn, addr, log_callback):
    data = conn.recv(4096).decode()
    log(f"Routeur connecté depuis {addr}", log_callback)

    try:
        rid, key, port = data.split("|")
        port = int(port)
    except:
        log("Format routeur invalide", log_callback)
        return

    with routeurs_lock:
        routeurs[rid] = {
        "ip": addr[0],
        "port": port,
        "key": key
    }


    conn_db = connect_bdd()
    cur = conn_db.cursor()
    cur.execute(
        "REPLACE INTO routeurs (id, ip, port, cle_publique) VALUES (?, ?, ?, ?)",
        (rid, addr[0], port, key)
    )
    conn_db.commit()
    conn_db.close()

    log(f"Routeur {rid} enregistré", log_callback)
    conn.send(b"OK")
    conn.close()

def router_server(log_callback):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, ROUTER_PORT))
        server.listen()
        log("Serveur routeurs actif", log_callback)
    except Exception as e:
        log(f"Erreur bind routeurs : {e}", log_callback)
        return

    while server_running:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_router,
            args=(conn, addr, log_callback),
            daemon=True
        ).start()


# =====================================================
# CLIENTS
# =====================================================
def handle_client(conn, addr, log_callback):
    log(f"Client connecté depuis {addr}", log_callback)

    with routeurs_lock:
        log(f"Envoi de {len(routeurs)} routeur(s) au client", log_callback)

        for rid, r in routeurs.items():
            line = f"{rid};{r['ip']};{r['port']};{r['key']}\n"
            conn.send(line.encode())

    conn.send(b"END")
    conn.close()




def client_server(log_callback):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, CLIENT_PORT))
        server.listen()
        log("Serveur clients actif", log_callback)
    except Exception as e:
        log(f"Erreur bind clients : {e}", log_callback)
        return

    while server_running:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr, log_callback),
            daemon=True
        ).start()


# =====================================================
# LANCEMENT GLOBAL
# =====================================================
def start_master_server(log_callback=None):
    threading.Thread(
        target=router_server,
        args=(log_callback,),
        daemon=True
    ).start()

    threading.Thread(
        target=client_server,
        args=(log_callback,),
        daemon=True
    ).start()

def get_routeurs_snapshot():
    """
    Retourne une copie de l'état des routeurs (thread-safe).
    Utilisé par l'interface graphique.
    """
    with routeurs_lock:
        return dict(routeurs)
    
# =====================================================
# API POUR L'INTERFACE GRAPHIQUE
# =====================================================

def start_master(log_callback=None):
    """
    Point d'entrée utilisé par l'interface graphique
    """
    start_master_server(log_callback)
