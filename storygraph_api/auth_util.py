import os
import platform
import sqlite3
from pathlib import Path
import keyring
from cryptography.hazmat.backends import default_backend
from subprocess import Popen, PIPE
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
import base64

def get_encryption_key():
    cmd = ['security', 'find-generic-password', '-w', '-a', 'Chrome', '-s', 'Chrome Safe Storage']
    return Popen(cmd, stdout=PIPE).stdout.read().strip()


def decrypt_cookie(encrypted_cookie, encryption_key):
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16
    iterations = 1003

    iv = encrypted_cookie[:AES.block_size]
    ct = encrypted_cookie[AES.block_size:]
    encrypted_cookie = encrypted_cookie[3:]  # Trim prefix 'v10'
    encrypted_cookie = encrypted_cookie[AES.block_size:]

    key = PBKDF2(encryption_key, salt, length, iterations)
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted_value = cipher.decrypt(encrypted_cookie)
    print(f"F0: {decrypted_value}")
    decrypted_value = unpad(decrypted_value, AES.block_size)
    print(f"F1: {decrypted_value}")

    decoded_bytes = base64.b64decode(decrypted_value)
    decoded_string = decoded_bytes.decode('utf8')
    print(decoded_string)
    
    return decoded_string

def get_user_token_cookie():
    """
    Retrieves the 'remember_user_token' cookie for domains ending with 'thestorygraph.com'
    from Google Chrome's cookie store on macOS.
    Raises an OSError if the current OS isn't macOS.
    """
    if platform.system() != "Darwin":
        raise OSError("Only macOS is supported.")

    # Path to Chrome's Cookies database on macOS
    cookies_path = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Cookies"
    if not cookies_path.exists():
        raise FileNotFoundError("Chrome Cookies database not found.")

    key = get_encryption_key()

    connection = sqlite3.connect(str(cookies_path))
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT encrypted_value
            FROM cookies
            WHERE host_key LIKE '%thestorygraph.com'
            AND name = 'remember_user_token'
            ORDER BY expires_utc DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            encrypted_value = row[0]
            return decrypt_cookie(encrypted_value, key)
        return None
    finally:
        connection.close()