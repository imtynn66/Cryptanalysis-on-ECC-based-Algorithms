import random
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# Curve parameters
p = 1331169830894825846283645180581
a = -35
b = 98

# Setup curve
E = EllipticCurve(GF(p), [a, b])
# Generator
gx = 479691812266187139164535778017
gy = 568535594075310466177352868412

G=E((gx,gy))
# Alice's Public Key
P = E((1110072782478160369250829345256, 800079550745409318906383650948))

P2 = E((1290982289093010194550717223760, 762857612860564354370535420319))

# Find the embedding degree of the curve
# Smallest k such that order of G divides p^k -1 
order = G.order()
k = 1
while (p**k - 1) % order:
    k += 1
print(k)

# Form Elliptic Curve in extended field
K.<a> = GF(p**k)
EK = E.base_extend(K)
# Corresponding points in this extended field
PK = EK(P)
GK = EK(G)

# Find Q in this extended field which is linearly independent to P 

R = EK.random_point()
m = R.order()
d = gcd(m, G.order())
Q = (m//d)*R

print("Pairing points  to F*p^k")
# Can also use Weil pairing here , that does not require k

AA = PK.tate_pairing(Q, G.order(),k)
GG = GK.tate_pairing(Q, G.order(),k)

print("DLP solving initiated......")
# Solving in finite field F*(p^k) 
dlA = AA.log(GG)
# We get Alice's secret
print(dlA)
# from source import gen_shared_secret
def gen_shared_secret(P, n):
    S = P*n
    return S.xy()[0]


S2 = gen_shared_secret(P2, dlA)

def decrypt_flag(shared_secret: int, iv, ct):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Decrypt flag
    iv = bytes.fromhex(iv)
    ct = bytes.fromhex(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ct)

    return plaintext

data =  {'iv': 'eac58c26203c04f68d63dc2c58d79aca', 'ct': 'bb9ecbd3662d0671fd222ccb07e27b5500f304e3621a6f8e9c815bc8e4e6ee6ebc718ce9ca115cb4e41acb90dbcabb0d'}


flag = decrypt_flag(S2, data['iv'], data['ct'])

print(flag)