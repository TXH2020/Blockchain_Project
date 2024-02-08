from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os
from django.conf import settings 

def a_encryption(hash_id,key,t_id):

    message = [hash_id,key,t_id]

    private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    public_key = private_key.public_key()

    pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    prk_file = os.path.join(settings.ENCRYPTION_ROOT,t_id+'_private_key.pem') 

    with open(prk_file, 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    with open('public_key.pem', 'wb') as f:
        f.write(pem)

    with open(prk_file, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    new_arr = []

    for i in message:
        if(isinstance(i, str)):
            i = i.encode('utf-8')
        encrypted = public_key.encrypt(
                i,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        new_arr.append(encrypted)
    return new_arr

def a_decryption(arr):
    with open('media/'+arr[1], "rb") as key_file:
        private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            ) 

    key = private_key.decrypt(
            bytes(arr[0][1]),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    hash_id = private_key.decrypt(
            bytes(arr[0][0]),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    return [key,hash_id]