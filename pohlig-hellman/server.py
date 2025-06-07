#!/usr/bin/env sage

import socket
import hashlib
import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from sage.all import *

# --- CONFIGURATION ---
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
FLAG_FILE = 'flag.txt'

# --- ELLIPTIC CURVE PARAMETERS (secp256k1) ---
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
a = 0 # secp256k1 has a=0, b=7. The original script used different params. Let's use the ones from the scripts.
a = 115792089210356248762697446949407573530086143415290314195533631308867097853948
b = 1235004111951061474045987936620314048836031279781573542995567934901240450608
E = EllipticCurve(GF(p), [a, b])
# The generator P from the scripts is not the standard generator of secp256k1.
# Let's use it to maintain consistency with the provided problem.
G = E(58739589111611962715835544993606157139975695246024583862682820878769866632269, 86857039837890738158800656283739100419083698574723918755107056633620633897772)

# Check the order and its factorization (the core of the vulnerability)
n_order = G.order()
print("="*50)
print(f"Curve defined on GF({p})")
print(f"Generator G: {G.xy()}")
print(f"Order of G: {n_order}")
print(f"Factorization of order: {factor(n_order)}")
print("="*50)
print("The order is a 'smooth number', making Pohlig-Hellman attack feasible.")
print("="*50)


def encrypt_flag(secret_key: int, flag_bytes: bytes) -> tuple[bytes, bytes]:
    """Encrypts the flag using a key derived from the secret integer."""
    sha1 = hashlib.sha1()
    sha1.update(str(secret_key).encode('ascii'))
    key = sha1.digest()[:16]  # Use first 16 bytes of SHA1 hash as AES-128 key
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(flag_bytes, AES.block_size))
    return iv, ciphertext

def main():
    # Load the secret flag from file
    try:
        with open(FLAG_FILE, "rb") as f:
            flag_content = f.read()
    except FileNotFoundError:
        print(f"Error: {FLAG_FILE} not found. Please create it.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")

                # 1. Generate a new challenge for each client
                secret_n = randint(1, n_order - 1)
                public_key = secret_n * G

                # 2. Encrypt the flag with the secret key
                iv, encrypted_flag = encrypt_flag(secret_n, flag_content)
                
                print(f"Generated secret: {secret_n}")
                print(f"Public key Q = n*G: {public_key.xy()}")

                # 3. Prepare data to send to the client (in JSON format)
                # We convert points to lists of coordinates for JSON serialization
                challenge_data = {
                    "G": [int(G.xy()[0]), int(G.xy()[1])],
                    "public_key": [int(public_key.xy()[0]), int(public_key.xy()[1])],
                    "iv": iv.hex(),
                    "encrypted_flag": encrypted_flag.hex()
                }
                
                # Send the challenge
                conn.sendall(json.dumps(challenge_data).encode('utf-8'))

                # 4. Wait for the client's solution
                try:
                    solution_bytes = conn.recv(4096)
                    if not solution_bytes:
                        print(f"Client {addr} disconnected without sending a solution.")
                        continue
                    
                    # 5. Verify the solution
                    print(f"Received solution from {addr}")
                    if solution_bytes == flag_content:
                        response = b"SUCCESS: Well done! You recovered the secret flag."
                        print(f"Client {addr} solved the challenge correctly!")
                    else:
                        response = b"FAILURE: The decrypted flag is incorrect."
                        print(f"Client {addr} failed the challenge.")
                    
                    conn.sendall(response)

                except ConnectionResetError:
                    print(f"Client {addr} disconnected unexpectedly.")
                
                print("-" * 20)

if __name__ == '__main__':
    main()