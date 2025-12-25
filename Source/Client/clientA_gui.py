import sys
import socket
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

# ================= CONFIG =================
CLIENT_ID = "A"
LISTEN_PORT = 7001

DEST_IP = "127.0.0.1"
DEST_PORT = 7000  # Client B

# =====================================================
# CLIENT GUI
# =====================================================
class ClientGUI(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.log_signal.connect(self.add_log)

        self.setWindowTitle("SAE3.02 - Client A")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Titre
        title = QLabel("Client A")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        # Champ message
        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("Message à envoyer...")
        layout.addWidget(self.input_message)

        # Bouton envoyer
        self.btn_send = QPushButton("Envoyer")
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        # Thème bleu nuit
        self.setStyleSheet("""
            QWidget { background-color:#0b1c2d; color:white; }
            QPushButton { background:#1f4e79; padding:8px; font-weight:bold; }
            QPushButton:hover { background:#2e6fa3; }
            QTextEdit { background:#12263a; }
            QLineEdit { background:#12263a; padding:6px; }
        """)

        # Démarrage du receiver
        threading.Thread(
            target=self.receiver_thread,
            daemon=True
        ).start()

        self.add_log(f"Client A en écoute sur le port {LISTEN_PORT}")

    # =================================================
    # THREAD RECEIVER (non bloquant)
    # =================================================
    def receiver_thread(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", LISTEN_PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            message = conn.recv(4096).decode()
            conn.close()

            self.log_signal.emit(
                f"Message reçu de {addr[0]}:{addr[1]} → {message}"
            )

    # =================================================
    # ENVOI MESSAGE (thread séparé)
    # =================================================
    def send_message(self):
        message = self.input_message.text().strip()

        if not message:
            return

        threading.Thread(
            target=self.send_thread,
            args=(message,),
            daemon=True
        ).start()

    def send_thread(self, message):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((DEST_IP, DEST_PORT))
            s.send(message.encode())
            s.close()

            self.log_signal.emit(
                f"Message envoyé vers {DEST_IP}:{DEST_PORT}"
            )
        except Exception as e:
            self.log_signal.emit(f"Erreur envoi : {e}")

    # =================================================
    # LOG
    # =================================================
    def add_log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {text}")


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ClientGUI()
    win.show()
    sys.exit(app.exec_())
