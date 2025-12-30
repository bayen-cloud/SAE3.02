import sys
import threading
import time
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
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

import master


class MasterGUI(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.log_signal.connect(self.ajouter_log)

        self.setWindowTitle("SAE3.02 - Master")
        self.setGeometry(200, 200, 900, 550)

        layout = QVBoxLayout()
        self.setLayout(layout)

        titre = QLabel("SAE3.02 - Master")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("font-size:20px;font-weight:bold;")
        layout.addWidget(titre)

        self.label_etat = QLabel("État : arrêté")
        self.label_etat.setStyleSheet("color:#d18b47;font-weight:bold;")
        layout.addWidget(self.label_etat)

        self.table_routeurs = QTableWidget()
        self.table_routeurs.setColumnCount(3)
        self.table_routeurs.setHorizontalHeaderLabels(
            ["ID Routeur", "Adresse IP", "Port"]
        )
        self.table_routeurs.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_routeurs)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        self.btn = QPushButton("Démarrer le Master")
        self.btn.clicked.connect(self.demarrer_master)
        layout.addWidget(self.btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.rafraichir_routeurs)
        self.timer.start(1000)

        # 🎨 THEME CARBON COPPER
        self.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #f2f2f2;
            font-family: Segoe UI;
        }
        QPushButton {
            background-color: #b87333;
            color: black;
            padding: 8px;
            border-radius: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d18b47;
        }
        QTextEdit, QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #3a3a3a;
            color: #f2f2f2;
        }
        QHeaderView::section {
            background-color: #3a3a3a;
            color: #f2f2f2;
            font-weight: bold;
        }
        """)

    def demarrer_master(self):
        self.btn.setEnabled(False)
        self.label_etat.setText("État : en cours d'exécution")
        threading.Thread(
            target=master.start_master,
            args=(self.log_signal.emit,),
            daemon=True
        ).start()
        self.ajouter_log("Master démarré")

    def rafraichir_routeurs(self):
        routeurs = master.get_routeurs_snapshot()
        self.table_routeurs.setRowCount(len(routeurs))
        for i, (rid, info) in enumerate(routeurs.items()):
            self.table_routeurs.setItem(i, 0, QTableWidgetItem(rid))
            self.table_routeurs.setItem(i, 1, QTableWidgetItem(info["ip"]))
            self.table_routeurs.setItem(i, 2, QTableWidgetItem(str(info["port"])))

    def ajouter_log(self, message):
        self.logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MasterGUI()
    win.show()
    sys.exit(app.exec_())
