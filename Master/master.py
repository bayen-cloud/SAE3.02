import socket
import threading

from database import Database
from parser import parse_message

MASTER_PORT = 5000

class MasterServer:

    def __init__(self):
        self.db = Database()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", MASTER_PORT))
        self.sock.listen(10)
        print("[MASTER] Écoute sur le port", MASTER_PORT)

    def start(self):
        while True:
            conn, addr = self.sock.accept()
            print("[MASTER] Connexion de :", addr)
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        try:
            raw = conn.recv(4096).decode()
            msg = parse_message(raw)

            if msg.get("TYPE") == "ROUTER":
                self.register_router(msg, addr)

            elif msg.get("TYPE") == "CLIENT":
                if msg.get("ACTION") == "GET_ROUTER_LIST":
                    self.send_router_list(conn)

        except Exception as e:
            print("[MASTER] Erreur:", e)

        finally:
            conn.close()

    def register_router(self, msg, addr):
        name = msg.get("NAME")
        port = msg.get("PORT")
        pubkey = msg.get("PUBLIC_KEY")
        ip = addr[0]

        self.db.add_router(name, ip, port, pubkey)
        print(f"[MASTER] Routeur enregistré : {name}@{ip}:{port}")

    def send_router_list(self, conn):
        routers = self.db.get_routers()

        response = ""
        for name, ip, port, pub in routers:
            response += f"ROUTER:{name}|{ip}|{port}|{pub}\n"

        response += "END\n"
        conn.send(response.encode())

        print("[MASTER] Liste des routeurs envoyée.")


if __name__ == "__main__":
    MasterServer().start()
