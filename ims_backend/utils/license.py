from Crypto.Cipher import AES

SECRET_KEY = b"A\x80'\ncX1\xbf\x10q\x9c\xbb\x17\xba\xa2\x9b"


def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]


def decrypt(encrypted_data):
    iv = encrypted_data[: AES.block_size]
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data[AES.block_size :])
    return unpad(decrypted_data).decode()
