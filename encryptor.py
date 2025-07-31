from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
import os

def derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).digest()

def generate_random_key() -> str:
    return os.urandom(16).hex()[:16]

def semantic_filename(message: str, media_type: str = "image") -> str:
    hash_value = hashlib.sha256(message.encode('utf-8')).hexdigest()
    extensions = {
        'image': '.png',
        'audio': '.wav', 
        'video': '.mp4'
    }
    ext = extensions.get(media_type.lower(), '.png')
    return f"stego_{hash_value[:10]}{ext}"

def get_message_preview(message: str, max_length: int = 20) -> str:
    if len(message) <= max_length:
        return message
    return message[:max_length] + "..."

def encrypt_message(message: str, password: str) -> str:
    try:
        key = derive_key(password)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(message.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_message)
        encrypted_with_iv = iv + encrypted_data
        return base64.b64encode(encrypted_with_iv).decode('utf-8')
    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")

def decrypt_message(encrypted_message: str, password: str) -> str:
    try:
        key = derive_key(password)
        encrypted_with_iv = base64.b64decode(encrypted_message.encode('utf-8'))
        iv = encrypted_with_iv[:16]
        encrypted_data = encrypted_with_iv[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_data)
        decrypted_message = unpad(decrypted_padded, AES.block_size)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")

def test_encryption():
    test_message = "The eagle lands at midnight"
    test_password = "test_password_123"
    print("Testing AES Encryption...")
    encrypted = encrypt_message(test_message, test_password)
    print(f"Encrypted: {encrypted[:50]}...")
    decrypted = decrypt_message(encrypted, test_password)
    print(f"Decrypted: {decrypted}")
    assert test_message == decrypted, "Encryption/Decryption test failed!"
    print("Encryption test passed!")
    auto_key = generate_random_key()
    print(f"Generated key: {auto_key}")
    filename = semantic_filename(test_message, "image")
    print(f"Semantic filename: {filename}")

if __name__ == "__main__":
    test_encryption()