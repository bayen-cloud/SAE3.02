import sys
import threading
import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt, QTimer

import master   # master.py


class MasterGUI(QWidget):
    log_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.log_signal.connect(self.ajouter_log)

        # -------------------------------------------------
        # Fenêtre principale
        # -------------------------------------------------
        self.setWindowTitle("SAE3.02 - Master")
        self.setGeometry(200, 200, 900, 550)

        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        # -------------------------------------------------
        # TITRE
        # -------------------------------------------------
        self.titre = QLabel("SAE3.02 - Master")
        self.titre.setAlignment(Qt.AlignCenter)
        self.titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout_principal.addWidget(self.titre)

        # -------------------------------------------------
        # ÉTAT DU MASTER
        # -------------------------------------------------
        self.label_etat = QLabel("État : arrêté")
        self.label_etat.setStyleSheet("color: #ff4c4c; font-weight: bold;")
        self.layout_principal.addWidget(self.label_etat)

        # -------------------------------------------------
        # TABLE DES ROUTEURS
        # -------------------------------------------------
        self.table_routeurs = QTableWidget()
        self.table_routeurs.setColumnCount(3)
        self.table_routeurs.setHorizontalHeaderLabels(
            ["ID Routeur", "Adresse IP", "Port"]
        )
        self.table_routeurs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout_principal.addWidget(self.table_routeurs)

        # -------------------------------------------------
        # ZONE DE LOGS
        # -------------------------------------------------
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setPlaceholderText("Journal du Master...")
        self.layout_principal.addWidget(self.logs)

        # -------------------------------------------------
        # BOUTON DÉMARRAGE
        # -------------------------------------------------
        self.bouton_demarrer = QPushButton("Démarrer le Master")
        self.bouton_demarrer.clicked.connect(self.demarrer_master)
        self.layout_principal.addWidget(self.bouton_demarrer)

        # -------------------------------------------------
        # TIMER DE RAFRAÎCHISSEMENT
        # -------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.rafraichir_routeurs)
        self.timer.start(1000)

        # -------------------------------------------------
        # THÈME BLEU NUIT
        # -------------------------------------------------
        self.setStyleSheet("""
            QWidget {
                background-color: #0b1c2d;
                color: #ffffff;
                font-family: Segoe UI;
            }

            QLabel {
                color: #ffffff;
            }

            QPushButton {
                background-color: #1f4e79;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2e6fa3;
            }

            QTableWidget {
                background-color: #12263a;
                color: white;
                gridline-color: #1f4e79;
            }

            QHeaderView::section {
                background-color: #1f4e79;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }

            QTextEdit {
                background-color: #12263a;
                color: white;
                border: 1px solid #1f4e79;
            }
        """)

    # -------------------------------------------------
    # DÉMARRAGE DU MASTER
    # -------------------------------------------------
    def demarrer_master(self):
        self.bouton_demarrer.setEnabled(False)
        self.label_etat.setText("État : en cours d'exécution")
        self.label_etat.setStyleSheet("color: #4caf50; font-weight: bold;")

        threading.Thread(
            target=master.start_master,
            args=(self.log_signal.emit,),
            daemon=True
        ).start()



        self.ajouter_log("Master démarré")

    # -------------------------------------------------
    # RAFRAÎCHISSEMENT DES ROUTEURS
    # -------------------------------------------------
    def rafraichir_routeurs(self):
        routeurs = master.get_routeurs_snapshot()

        self.table_routeurs.setRowCount(len(routeurs))

        for ligne, (rid, info) in enumerate(routeurs.items()):
            self.table_routeurs.setItem(
                ligne, 0, QTableWidgetItem(rid)
            )
            self.table_routeurs.setItem(
                ligne, 1, QTableWidgetItem(info["ip"])
            )
            self.table_routeurs.setItem(
                ligne, 2, QTableWidgetItem(str(info["port"]))
            )

    # -------------------------------------------------
    # AJOUT D'UN LOG
    # -------------------------------------------------
    def ajouter_log(self, message):
        heure = time.strftime("%H:%M:%S")
        self.logs.append(f"[{heure}] {message}")


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MasterGUI()
    fenetre.show()
    sys.exit(app.exec_())
