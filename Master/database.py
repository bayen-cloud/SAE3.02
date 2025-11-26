import mariadb

class Database:
    def __init__(self, host="192.168.56.4", user="toto", password="toto", database="badosae32"):
        try:
            self.conn = mariadb.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor()
            print("[DB] Connexion OK.")
        except mariadb.Error as e:
            print("[DB] Erreur :", e)
            exit(1)

    def add_router(self, name, ip, port, public_key):
        try:
            self.cursor.execute(
                "INSERT INTO routers (name, ip, port, public_key) VALUES (?, ?, ?, ?)",
                (name, ip, port, public_key)
            )
            self.conn.commit()
            print("[DB] Routeur ajouté :", name)
        except mariadb.Error as e:
            print("[DB] Erreur INSERT :", e)

    def get_routers(self):
        self.cursor.execute("SELECT name, ip, port, public_key FROM routers")
        return list(self.cursor)
