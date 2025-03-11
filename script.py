#!/usr/bin/env python3
import sys
import os
import subprocess
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        self.progress.emit(0)
        self.log.emit(f"Running: {' '.join(self.command)}\n")
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            self.log.emit(line)
        process.wait()
        self.progress.emit(100)
        self.log.emit("Task completed.\n")

class LinuxTroubleshooter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        commands = {
            "Check for updates": ["sudo", "apt", "update"],
            "Upgrade system": ["sudo", "apt", "upgrade", "-y"],
            "Fix broken dependencies": ["sudo", "apt", "--fix-broken", "install"],
            "Check disk space": ["df", "-h"],
            "Check network connectivity": ["ping", "-c", "4", "8.8.8.8"],
            "Clean system": ["sudo", "apt", "autoremove", "-y"],
            "Read system logs": ["sudo", "journalctl", "-n", "50"],
            "Remove problematic PPAs": ["sudo", "add-apt-repository", "--remove"],
            "Reboot system": ["sudo", "reboot"]
        }

        for label, command in commands.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, cmd=command: self.run_command(cmd))
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setWindowTitle("Linux Troubleshooter")
        self.setGeometry(100, 100, 600, 400)

    def run_command(self, command):
        self.thread = WorkerThread(command)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.log.connect(self.log_area.append)
        self.thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinuxTroubleshooter()
    window.show()
    sys.exit(app.exec())
