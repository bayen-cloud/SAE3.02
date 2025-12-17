import sys
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QMessageBox
)

# IMPORT DE TON CODE EXISTANT
# On suppose que clientA.py contient une fonction envoyer_message(message)
from clientA import envoyer_message


class ClientAGUI(QWidget):
    """
    Interface graphique du Client A
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client A - Envoi de message")
        self.setGeometry(200, 200, 400, 300)

        # Widgets
        self.label = QLabel("Message à envoyer :")
        self.text_message = QTextEdit()
        self.button_send = QPushButton("Envoyer")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.text_message)
        layout.addWidget(self.button_send)

        self.setLayout(layout)

        # Connexion bouton
        self.button_send.clicked.connect(self.on_send_clicked)

    def on_send_clicked(self):
        """
        Action lors du clic sur le bouton Envoyer
        """
        message = self.text_message.toPlainText().strip()

        if not message:
            QMessageBox.warning(self, "Erreur", "Le message est vide")
            return

        # Envoi non bloquant
        thread = threading.Thread(
            target=self.send_message_thread,
            args=(message,),
            daemon=True
        )
        thread.start()

        QMessageBox.information(self, "Succès", "Message envoyé")
        self.text_message.clear()

    def send_message_thread(self, message):
        """
        Thread d'envoi du message
        """
        try:
            envoyer_message(message)
        except Exception as e:
            print(f"[Client A GUI] Erreur envoi : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientAGUI()
    window.show()
    sys.exit(app.exec_())
