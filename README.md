# 📚 KindleDrop

*A Python tool for automatically sending PDFs to your Kindle via SFTP.*

---

## ✨ Description

**KindleDrop** is a lightweight, object-oriented Python utility that automates PDF delivery to your Kindle over an SFTP connection. With built-in logging, file tracking, and secure credentials via `.env`, it’s the easiest way to beam content to your Kindle without lifting a finger.

Perfect for readers who curate their own PDFs, want to bypass email-based delivery, or automate nightly drops of content.

---

## 🚀 Features

- 📁 Send all PDFs from a specified local folder
- 🔐 Secure connection using credentials stored in a `.env` file
- 🔍 Skips duplicates using both Kindle-side checks and a local sent log
- 📜 Logging to file for full transparency and debugging
- ✅ Clean object-oriented structure, easy to extend

---

## 🛠 Requirements

- Python 3.10
- [`paramiko`](https://pypi.org/project/paramiko/)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install paramiko python-dotenv
```

Please create a .env file in the root directory with the following fields
```bash
# .env file for KindleSFTP

# Kindle connection settings
KINDLE_IP=XXX.XXX.X.XX
KINDLE_PORT=2222
KINDLE_USERNAME=your_username
KINDLE_PASSWORD=your_password

# Local folder where PDFs are stored
SOURCE_FOLDER=/path/to/your/pdfs

# Remote folder on Kindle where PDFs should be sent
DEST_FOLDER=/documents

