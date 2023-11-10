import hashlib  # ф-ия для хэширования пароликов


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
