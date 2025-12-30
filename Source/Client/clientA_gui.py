import sys
import socket
import threading
import time
import client_oignon

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

LISTEN_PORT = 7001


class ClientGUI(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.log_signal.connect(self.add_log)

        self.setWindowTitle("SAE3.02 - Client A")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Client A")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Message à envoyer...")
        layout.addWidget(self.input)

        btn = QPushButton("Envoyer")
        btn.clicked.connect(self.send_message)
        layout.addWidget(btn)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        # 🎨 THEME
        self.setStyleSheet("""
        QWidget { background:#121212; color:#f2f2f2; }
        QPushButton {
            background:#d18b47;
            color:black;
            border-radius:8px;
            padding:8px;
            font-weight:bold;
        }
        QPushButton:hover { background:#b87333; }
        QTextEdit, QLineEdit {
            background:#1e1e1e;
            border:1px solid #3a3a3a;
            color:#f2f2f2;
        }
        """)

        threading.Thread(target=self.receiver, daemon=True).start()
        self.add_log(f"Client A en écoute sur {LISTEN_PORT}")

    def receiver(self):
        s = socket.socket()
        s.bind(("0.0.0.0", LISTEN_PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            msg = conn.recv(4096).decode()
            conn.close()
            self.log_signal.emit(f"Message reçu → {msg}")

    def send_message(self):
        msg = self.input.text().strip()
        if not msg:
            return
        self.input.clear()
        threading.Thread(target=self.send_thread, args=(msg,), daemon=True).start()

    def send_thread(self, msg):
        chemin = client_oignon.envoyer_message_oignon(msg, 7000)
        self.log_signal.emit(
            "Chemin utilisé : " + " → ".join(rid for rid, _ in chemin)
        )

    def add_log(self, txt):
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {txt}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ClientGUI()
    win.show()
    sys.exit(app.exec_())
