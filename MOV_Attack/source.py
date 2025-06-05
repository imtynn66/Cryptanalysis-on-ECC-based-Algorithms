import random
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

FLAG = b"crypto{??????????????????????????????????????}"

def gen_keypair(G, p):
    n = random.randint(1, (p-1))
    P = n*G
    return n, P

def gen_shared_secret(P, n):
    S = P*n
    return S.xy()[0]

def encrypt_flag(shared_secret: int):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Encrypt flag
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(FLAG, 16))
    # Prepare data to send
    data = {}
    data['iv'] = iv.hex()
    data['encrypted_flag'] = ciphertext.hex()
    return data

# Define Curve params
p = 1331169830894825846283645180581
a = -35
b = 98
E = EllipticCurve(GF(p), [a,b])
G = E.gens()[0]

# Generate keypair
n_a, P1 = gen_keypair(G, p)
n_b, P2 = gen_keypair(G, p)

# Calculate shared secret
S1 = gen_shared_secret(P1, n_b)
S2 = gen_shared_secret(P2, n_a)

# Check protocol works
assert S1 == S2

flag = encrypt_flag(S1)

print(f"Generator: {G}")
print(f"Alice Public key: {P1}")
print(f"Bob Public key: {P2}")
print(f"Encrypted flag: {flag}")

# Generator: (479691812266187139164535778017 : 568535594075310466177352868412 : 1)
# Alice Public key: (1110072782478160369250829345256 : 800079550745409318906383650948 : 1)
# Bob Public key: (1290982289093010194550717223760 : 762857612860564354370535420319 : 1)
# Encrypted flag: {'iv': 'eac58c26203c04f68d63dc2c58d79aca', 'encrypted_flag': 'bb9ecbd3662d0671fd222ccb07e27b5500f304e3621a6f8e9c815bc8e4e6ee6ebc718ce9ca115cb4e41acb90dbcabb0d'}
