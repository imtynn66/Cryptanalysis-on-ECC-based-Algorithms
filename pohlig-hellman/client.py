#!/usr/bin/env sage

import socket
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sage.all import *
from tqdm import tqdm

# --- SERVER CONFIGURATION ---
HOST = '127.0.0.1'
PORT = 65432

# --- ELLIPTIC CURVE PARAMETERS (must match server) ---
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
a = 115792089210356248762697446949407573530086143415290314195533631308867097853948
b = 1235004111951061474045987936620314048836031279781573542995567934901240450608
E = EllipticCurve(GF(p), [a, b])

def solve_ecdlp_pohlig_hellman(P, Q):
    """
    Solves the ECDLP Q = x*P using the Pohlig-Hellman algorithm.
    This is efficient because the order of P is a smooth number.
    """
    n = P.order()
    print(f"[*] Order of P: {n}")
    
    prime_factors = factor(n)
    print(f"[*] Prime factors of order: {prime_factors}")
    
    congruences = []
    moduli = []

    print("[*] Solving DLP for each prime factor subgroup...")
    for prime, exponent in tqdm(prime_factors):
        modulus = prime ** exponent
        
        # Project P and Q into the subgroup of order p^e
        order_subgroup = n // modulus
        P_sub = order_subgroup * P
        Q_sub = order_subgroup * Q
        
        # Solve the DLP in the smaller subgroup
        # discrete_log is fast here because the order of P_sub is a prime power
        x_sub = discrete_log(Q_sub, P_sub, operation='+')
        
        congruences.append(x_sub)
        moduli.append(modulus)
        print(f"    - Found x = {x_sub} (mod {modulus})")

    # Combine the results using the Chinese Remainder Theorem (CRT)
    print("\n[*] Combining results using Chinese Remainder Theorem (CRT)...")
    secret = crt(congruences, moduli)
    
    print(f"[*] Recovered Secret: {secret}")
    
    # Verification
    assert secret * P == Q
    print("[+] Verification successful: secret * P == Q")
    
    return secret

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server at {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected!")

        # 1. Receive challenge data from the server
        print("\n[1] Receiving challenge from server...")
        data_bytes = s.recv(4096) # Buffer size
        challenge_data = json.loads(data_bytes.decode('utf-8'))

        # Reconstruct curve points from received coordinates
        G = E(challenge_data['G'][0], challenge_data['G'][1])
        public_key_Q = E(challenge_data['public_key'][0], challenge_data['public_key'][1])
        iv = bytes.fromhex(challenge_data['iv'])
        encrypted_flag = bytes.fromhex(challenge_data['encrypted_flag'])

        print(f"    - Received G: {G.xy()}")
        print(f"    - Received Public Key Q: {public_key_Q.xy()}")

        # 2. Solve the Elliptic Curve Discrete Logarithm Problem
        print("\n[2] Solving ECDLP to find the secret 'n'...")
        recovered_secret = solve_ecdlp_pohlig_hellman(G, public_key_Q)

        # 3. Decrypt the flag
        print("\n[3] Decrypting the flag using the recovered secret...")
        sha1 = hashlib.sha1()
        sha1.update(str(recovered_secret).encode('ascii'))
        key = sha1.digest()[:16]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_flag = cipher.decrypt(encrypted_flag)
        
        # Unpad the decrypted data
        try:
            decrypted_flag = unpad(decrypted_padded_flag, AES.block_size)
            print(f"[*] Decrypted flag (bytes): {decrypted_flag}")
        except ValueError as e:
            print(f"Error unpadding the flag: {e}")
            print("This usually means the decryption key was wrong.")
            return

        # 4. Send the solution back to the server
        print("\n[4] Sending decrypted flag to server for verification...")
        s.sendall(decrypted_flag)

        # 5. Receive and print the final result from the server
        response = s.recv(1024)
        print("\n[5] Server response:")
        print(f"    {response.decode('utf-8')}")

if __name__ == '__main__':
    main()