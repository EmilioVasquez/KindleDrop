import os
import paramiko
import logging
from dotenv import load_dotenv

class KindleSFTP:
    def __init__(self, env_path=".env", log_file="kindle_transfer.log", sent_log_file="sent_log.txt"):
        load_dotenv(env_path)
        self.host = os.getenv("KINDLE_IP")
        self.username = os.getenv("KINDLE_USERNAME")
        self.password = os.getenv("KINDLE_PASSWORD")
        self.source_folder = os.getenv("SOURCE_FOLDER")
        self.dest_folder = os.getenv("DEST_FOLDER")
        self.sent_log_file = sent_log_file

        self.transport = None
        self.sftp = None

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    def connect(self):
        try:
            self.transport = paramiko.Transport((self.host, 22))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logging.info("Connected to Kindle via SFTP.")
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            self.disconnect()
            raise

    def get_existing_remote_files(self):
        try:
            return self.sftp.listdir(self.dest_folder)
        except Exception as e:
            logging.error(f"Failed to list remote folder: {e}")
            return []

    def load_sent_log(self):
        if not os.path.exists(self.sent_log_file):
            return set()
        with open(self.sent_log_file, 'r') as f:
            return set(line.strip() for line in f)

    def update_sent_log(self, filename):
        with open(self.sent_log_file, 'a') as f:
            f.write(f"{filename}\n")

    def send_pdfs(self):
        try:
            local_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(".pdf")]
            remote_files = self.get_existing_remote_files()
            already_sent = self.load_sent_log()

            to_send = [f for f in local_files if f not in remote_files and f not in already_sent]

            if not to_send:
                logging.info("No new PDF files to send.")
                return

            for filename in to_send:
                local_path = os.path.join(self.source_folder, filename)
                remote_path = os.path.join(self.dest_folder, filename)

                self.sftp.put(local_path, remote_path)
                logging.info(f"Sent: {filename}")
                self.update_sent_log(filename)

        except Exception as e:
            logging.error(f"Failed during file transfer: {e}")
            raise

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        logging.info("Disconnected from Kindle.")
