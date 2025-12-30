import sys
import time
import threading
import clientB
import client_oignon

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer


class ClientBGUI(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.log_signal.connect(self.add_log)

        self.setWindowTitle("SAE3.02 - Client B")
        self.setGeometry(300, 300, 500, 450)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Client B")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Message vers Client A...")
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
            background:#8c4f1d;
            color:#f2f2f2;
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

        QTimer.singleShot(100, self.start_receiver)

    def start_receiver(self):
        clientB.start_client_b(self.log_signal.emit)
        self.add_log("Client B en écoute sur le port 7000")

    def send_message(self):
        msg = self.input.text().strip()
        if not msg:
            return
        self.input.clear()
        threading.Thread(target=self.send_thread, args=(msg,), daemon=True).start()

    def send_thread(self, msg):
        chemin = client_oignon.envoyer_message_oignon(msg, 7001)
        self.log_signal.emit(
            "Chemin utilisé : " + " → ".join(rid for rid, _ in chemin)
        )

    def add_log(self, txt):
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {txt}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ClientBGUI()
    win.show()
    sys.exit(app.exec_())
