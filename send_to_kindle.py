import logging
import os
from logging.handlers import TimedRotatingFileHandler
from sftp_handler import KindleSFTP

def setup_logging():
    # Create logs directory
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Clear existing handlers (important when running repeatedly)
    root.handlers.clear()

    # Common formatter
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Daily rotating file handler (keep 7 days)
    fh_path = os.path.join(log_dir, "kindle_transfer.log")
    fh = TimedRotatingFileHandler(
        fh_path, when="midnight", backupCount=7, encoding="utf-8"
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    # (Optional) quiet noisy libraries
    logging.getLogger("paramiko").setLevel(logging.WARNING)

def main():
    setup_logging()
    logger = logging.getLogger("kindle.main")
    logger.info("Starting Kindle SFTP transfer")

    kindle = KindleSFTP()  # no logger needed; module gets its own
    try:
        kindle.connect()
        kindle.send_pdfs()
    except Exception as e:
        logger.exception("Run failed: %s", e)
        raise
    finally:
        kindle.disconnect()
        logger.info("Finished Kindle SFTP transfer")

if __name__ == "__main__":
    main()
