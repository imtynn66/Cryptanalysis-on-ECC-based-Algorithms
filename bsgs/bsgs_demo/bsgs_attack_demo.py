import math
import time
import gmpy2
from ecc_helper import Point, G, scalar_mult, point_add, P

def bsgs_attack(public_key, n_max):
    """
    Baby-Step Giant-Step attack on ECC
    public_key: Point object representing public key
    n_max: maximum possible value for private key
    """
    print("[+] Starting BSGS attack...")
    start_time = time.time()
    
    # Calculate m = ceil(sqrt(n))
    m = math.ceil(math.sqrt(n_max))
    print(f"[+] Using m = {m} (sqrt of {n_max})")
    
    # Baby steps: calculate and store g^j for j in [0,m)
    print("[+] Computing baby steps...")
    baby_steps = {}
    for j in range(m):
        if j % 100000 == 0:
            print(f"    Progress: {j}/{m}")
        P = scalar_mult(j, G)
        baby_steps[P.x] = j
    
    # Precompute -mG for giant steps
    mG = scalar_mult(m, G)
    neg_mG = -mG
    
    # Giant steps: try h * g^(-m*i) for i in [0,m)
    print("[+] Computing giant steps...")
    Q = public_key
    for i in range(m):
        if i % 100000 == 0:
            print(f"    Progress: {i}/{m}")
            
        # Check if current point's x-coordinate is in baby_steps
        if Q.x in baby_steps:
            j = baby_steps[Q.x]
            private_key = i * m + j
            print(f"\n[+] Found private key: {private_key} (0x{hex(private_key)[2:]})")
            print(f"[+] Time taken: {time.time() - start_time:.2f} seconds")
            return private_key
            
        # Q = Q - mG
        Q = point_add(Q, neg_mG)
    
    print("\n[-] Private key not found")
    return None

def demo_attack():
    # Demo với private key nhỏ
    private_key = 4873205 # 0x76F98
    print(f"[+] Generating demo key pair with private key: {private_key} (0x{hex(private_key)[2:]})")
    
    # Generate public key
    public_key = scalar_mult(private_key, G)
    print(f"[+] Public key: {public_key}")
    
    # Set search range
    n_max = 1000000000  # Tìm trong khoảng [0, 10000000000000000)
    
    # Run attack
    found_key = bsgs_attack(public_key, n_max)
    
    if found_key == private_key:
        print("[+] Attack successful! Found correct private key.")
    else:
        print("[-] Attack failed or found incorrect key.")

if __name__ == "__main__":
    demo_attack() 