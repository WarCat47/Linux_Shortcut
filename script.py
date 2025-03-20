#!/usr/bin/env python3
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar, QFileDialog, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        self.progress.emit(0)
        self.log.emit(f"Running: {' '.join(self.command)}\n")
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                self.log.emit(line.strip())
            _, error = process.communicate()
            if process.returncode == 0:
                self.log.emit("✅ Task completed successfully.\n")
            else:
                self.log.emit(f"❌ Error occurred:\n{error.strip()}\n")
        except Exception as e:
            self.log.emit(f"❌ Exception: {str(e)}\n")
        self.progress.emit(100)

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

        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QFrame()
        scroll_layout = QVBoxLayout(scroll_content)

        commands = {
            "Check for updates": ["sudo", "apt", "update"],
            "Upgrade system": ["sudo", "apt", "upgrade", "-y"],
            "Fix broken dependencies": ["sudo", "apt", "--fix-broken", "install"],
            "Check disk space": ["df", "-h"],
            "Remove Problematic PPAs": ["sudo", "add-apt-repository", "--remove"],
            "Clean system": ["sudo", "apt", "autoremove", "-y"],
            "Read system logs": ["sudo", "journalctl", "-n", "50"],
            "Reboot system": ["sudo", "reboot"],
            "Check Failed Services": ["systemctl", "list-units", "--failed"],
            "Boot into Recovery Mode": ["sudo", "systemctl", "reboot", "--recovery"]
        }

        for label, command in commands.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, cmd=command: self.run_command(cmd))
            scroll_layout.addWidget(btn)  # Add to scroll_layout instead of layout

        # Install .deb file button
        install_deb_btn = QPushButton("Install .deb file")
        install_deb_btn.clicked.connect(self.install_deb)
        scroll_layout.addWidget(install_deb_btn)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)  # Add scroll area to main layout

        self.setLayout(layout)
        self.setWindowTitle("Linux Troubleshooter")
        self.setGeometry(100, 100, 600, 400)

    def run_command(self, command):
        self.thread = WorkerThread(command)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.log.connect(self.log_area.append)
        self.thread.start()

    def install_deb(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select .deb file", "", "Debian files (*.deb)")
        if file_path:
            package_name = self.get_package_name(file_path)
            if package_name and self.is_package_installed(package_name):
                QMessageBox.information(self, "Already Installed", f"{package_name} is already installed.")
                return
            self.run_command(["sudo", "apt", "install", file_path, "-y"])

    def get_package_name(self, file_path):
        try:
            output = subprocess.run(["dpkg-deb", "-I", file_path], capture_output=True, text=True).stdout
            for line in output.splitlines():
                if line.startswith(" Package:"):
                    return line.split(":")[1].strip()
        except Exception as e:
            self.log_area.append(f"❌ Failed to extract package name: {str(e)}")
        return None

    def is_package_installed(self, package_name):
        try:
            output = subprocess.run(["dpkg", "-s", package_name], capture_output=True, text=True).stdout
            return "Status: install ok installed" in output
        except Exception as e:
            self.log_area.append(f"❌ Failed to check if installed: {str(e)}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinuxTroubleshooter()
    window.show()
    sys.exit(app.exec())
