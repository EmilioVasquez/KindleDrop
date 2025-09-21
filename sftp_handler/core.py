import os
import paramiko
import logging
from dotenv import load_dotenv
import posixpath

logger = logging.getLogger("kindle.sftp")  # child logger for this module

class KindleSFTP:
    def __init__(self, env_path=".env", sent_log_file="sent_log.txt"):
        load_dotenv(env_path)

        # Helpers
        def _clean_local_path(p):
            if not p:
                return p
            p = p.strip().strip('"').strip("'")
            return os.path.normpath(p)

        def _to_posix(p):
            if not p:
                return p
            return posixpath.normpath(p.strip().strip('"').strip("'"))

        self.host = os.getenv("KINDLE_IP")
        self.port = int(os.getenv("KINDLE_PORT", "22"))
        self.username = os.getenv("KINDLE_USERNAME")
        self.password = os.getenv("KINDLE_PASSWORD")
        self.source_folder = _clean_local_path(os.getenv("SOURCE_FOLDER"))
        # Force POSIX for remote (Kindle/Linux)
        self.dest_folder = _to_posix(os.getenv("DEST_FOLDER"))
        self.sent_log_file = sent_log_file

        self.transport = None
        self.sftp = None

        # Basic sanity checks
        if not self.source_folder or not os.path.isdir(self.source_folder):
            raise OSError(f"Source folder does not exist or is invalid: {self.source_folder!r}")
        if not self.dest_folder or not self.dest_folder.startswith("/"):
            raise OSError(f"DEST_FOLDER must be an absolute POSIX path (e.g., /mnt/us/documents): {self.dest_folder!r}")

    def connect(self):
        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("Connected to Kindle via SFTP (%s:%s)", self.host, self.port)
        except Exception as e:
            logger.exception("Failed to connect: %s", e)
            self.disconnect()
            raise

    def get_existing_remote_files(self):
        try:
            files = self.sftp.listdir(self.dest_folder)
            logger.info("Remote folder '%s' contains %d files", self.dest_folder, len(files))
            return files
        except Exception as e:
            logger.exception("Failed to list remote folder '%s': %s", self.dest_folder, e)
            return []

    def load_sent_log(self):
        if not os.path.exists(self.sent_log_file):
            logger.info("No sent log found; starting fresh (%s)", self.sent_log_file)
            return set()
        with open(self.sent_log_file, 'r', encoding="utf-8") as f:
            items = set(line.strip() for line in f if line.strip())
            logger.info("Loaded %d entries from sent log", len(items))
            return items

    def update_sent_log(self, filename):
        with open(self.sent_log_file, 'a', encoding="utf-8") as f:
            f.write(f"{filename}\n")
        logger.info("Updated sent log with: %s", filename)

    def verify_transfers(self, filenames):
        """Log presence and size of transferred files on the device."""
        try:
            remote = set(self.sftp.listdir(self.dest_folder))
            for name in filenames:
                if name in remote:
                    remote_path = posixpath.join(self.dest_folder, name)
                    st = self.sftp.stat(remote_path)
                    logger.info("Verified on device: %s (%d bytes)", name, st.st_size)
                else:
                    logger.warning("Not found after transfer: %s", name)
        except Exception as e:
            logger.exception("Verification failed: %s", e)

    def send_pdfs(self):
        try:
            local_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(".pdf")]
            logger.info("Found %d local PDFs in '%s'", len(local_files), self.source_folder)

            remote_files = self.get_existing_remote_files()
            already_sent = self.load_sent_log()

            to_send = [f for f in local_files if f not in remote_files and f not in already_sent]
            logger.info("Queued %d new PDFs for transfer", len(to_send))

            if not to_send:
                logger.info("No new PDF files to send.")
                return

            for filename in to_send:
                # Windows-safe local path
                local_path = os.path.normpath(os.path.join(self.source_folder, filename))
                # POSIX remote path (always forward slashes)
                remote_path = posixpath.join(self.dest_folder, filename)

                self.sftp.put(local_path, remote_path)
                logger.info("Sent: %s", filename)
                self.update_sent_log(filename)

            # Optional: verify presence/sizes on device
            self.verify_transfers(to_send)

        except Exception as e:
            logger.exception("Failed during file transfer: %s", e)
            raise

    def disconnect(self):
        try:
            if self.sftp:
                self.sftp.close()
                self.sftp = None
            if self.transport:
                self.transport.close()
                self.transport = None
        finally:
            logger.info("Disconnected from Kindle")
