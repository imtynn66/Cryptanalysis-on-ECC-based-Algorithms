import math
import time
from sage.all import discrete_log
from server import Server, Client, a, b, p, n

def print_point(P, label=""):
    """In điểm trên đường cong một cách đẹp hơn"""
    if label:
        print(f"{label}:")
        print(f"    x = {hex(P[0])}")
        print(f"    y = {hex(P[1])}")
    else:
        print(f"x = {hex(P[0])}")
        print(f"y = {hex(P[1])}")

def format_num(num):
    """Format số lớn thành dạng hex cho dễ đọc"""
    return hex(num)

def bsgs_attack(curve, G, public_key, n_max):
    """
    Baby-Step Giant-Step attack on Anomalous curve với hiển thị chi tiết các bước tính toán
    curve: EllipticCurve object
    G: Generator point
    public_key: Public key point (target point H)
    n_max: maximum possible value for private key
    """
    print("\n=== Baby-Step Giant-Step Attack Details ===")
    print("[+] Problem Statement:")
    print("    Given: H = kG where k is unknown")
    print("\n[+] Generator point G:")
    print_point(G)
    print("\n[+] Public key H:")
    print_point(public_key)
    print(f"\n[+] Find k in range [1, {format_num(n_max)}]")
    
    start_time = time.time()
    
    # Calculate m = ceil(sqrt(n))
    m = math.ceil(math.sqrt(n_max))
    print(f"\n[+] Step 1: Calculate m = ceil(sqrt(n))")
    print(f"    m = {format_num(m)}")
    
    print("\n[+] Step 2: Baby Steps - Calculate and store jG for j in [0, m)")
    print("    Formula: Store (jG, j) in table where j = 0,1,2,...,m-1")
    baby_steps = {}
    print("\n    First few baby steps:")
    for j in range(m):
        P = j * G  # Calculate jG
        baby_steps[P[0]] = j  # Store x-coordinate
        
        # Print first few steps for demonstration
        if j < 3:  # Reduced from 5 to 3 due to larger numbers
            print(f"\n    j = {format_num(j)}:")
            print("    jG:")
            print_point(P)
        elif j == 3:
            print("\n    ... (continuing for all j up to m-1) ...")
    
    print(f"\n[+] Step 3: Precompute -mG for giant steps")
    mG = -m * G
    print("    -mG:")
    print_point(mG)
    
    print("\n[+] Step 4: Giant Steps - Calculate H + i(-mG) for i in [0, m)")
    print("    Formula: For each i, check if H + i(-mG) is in baby_steps table")
    Q = public_key  # Start with H
    print("\n    Giant step iterations:")
    for i in range(m):
        if i < 3:  # Reduced from 5 to 3 due to larger numbers
            print(f"\n    i = {format_num(i)}:")
            print("    Current point:")
            print_point(Q)
            
            if Q[0] in baby_steps:
                j = baby_steps[Q[0]]
                print(f"    Found match with baby step j = {format_num(j)}!")
                private_key = i * m + j
                print(f"    Checking k = i*m + j = {format_num(i)}*{format_num(m)} + {format_num(j)}")
                print(f"    k = {format_num(private_key)}")
                
                # Verify
                if private_key * G == public_key:
                    print(f"\n[+] Solution verified!")
                    print(f"[+] Found private key k = {format_num(private_key)}")
                    print(f"[+] Time taken: {time.time() - start_time:.2f} seconds")
                    return private_key
                else:
                    print(f"    False positive - continuing search")
        
        elif i == 3:
            print("\n    ... (continuing for all i up to m-1) ...")
        
        if Q[0] in baby_steps and i >= 3:
            j = baby_steps[Q[0]]
            private_key = i * m + j
            
            # Verify
            if private_key * G == public_key:
                print(f"\n[+] Solution found!")
                print(f"    i = {format_num(i)}")
                print(f"    j = {format_num(j)}")
                print(f"    k = i*m + j = {format_num(private_key)}")
                print(f"[+] Time taken: {time.time() - start_time:.2f} seconds")
                return private_key
        
        # Move to next giant step: Q = Q + (-mG)
        Q = Q + mG
    
    print("\n[-] Private key not found in given range")
    print(f"[+] Time taken: {time.time() - start_time:.2f} seconds")
    return None

def demo_attack():
    print("[+] Setting up ECDH demo for attack...")
    print(f"[+] Using anomalous curve with parameters:")
    print(f"    a = {format_num(a)}")
    print(f"    b = {format_num(b)}")
    print(f"    p = {format_num(p)}")
    print(f"    n = {format_num(n)}")
    
    # Khởi tạo server (victim)
    server = Server(a, b, p)
    client = Client(server)
    
    # Attacker nhận được public params
    params = server.get_public_params()
    curve = params['curve']
    G = params['G']
    public_key = params['public_key']
    
    print("\n[+] Target information:")
    print("\nGenerator G:")
    print_point(G)
    print("\nPublic key:")
    print_point(public_key)
    print(f"\nTrue private key: {format_num(server.private_key)}")
    
    # Thực hiện tấn công
    recovered_key = bsgs_attack(curve, G, public_key, n)
    
    # Xác minh kết quả
    if recovered_key is not None:
        if recovered_key == server.private_key:
            print("\n[+] Attack successful!")
            print(f"[+] Recovered key matches true private key:")
            print(f"    k = {format_num(recovered_key)}")
            # Xác minh thêm bằng cách tính public key
            computed_public = recovered_key * G
            if computed_public == public_key:
                print("[+] Verified: Recovered key generates correct public key")
        else:
            print("\n[-] Attack failed - recovered key does not match true private key")
            print(f"    Expected: {format_num(server.private_key)}")
            print(f"    Got: {format_num(recovered_key)}")
    else:
        print("\n[-] Attack failed - no key found in given range")

if __name__ == "__main__":
    demo_attack()