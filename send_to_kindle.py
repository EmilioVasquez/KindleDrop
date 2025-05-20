from sftp_handler import KindleSFTP

def main():
    kindle = KindleSFTP()
    try:
        kindle.connect()
        kindle.send_pdfs()
    finally:
        kindle.disconnect()

if __name__ == "__main__":
    main()
