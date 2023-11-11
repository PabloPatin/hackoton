import hashlib


def hash_string(input_string, algorithm='sha256'):
    hash_object = hashlib.new(algorithm)
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()
