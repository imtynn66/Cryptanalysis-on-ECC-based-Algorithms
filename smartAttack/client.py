#!/usr/bin/env python3
from sage.all import *
import socket
import json
import random
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import time

class SmartAttackClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def send_request(self, request):
        try:
            self.socket.send(json.dumps(request).encode())
            response = self.socket.recv(8192).decode()  
            if response:
                return json.loads(response)
            else:
                print("Empty response from server")
                return None
        except Exception as e:
            print(f"Communication error: {e}")
            return None
            
    def get_server_info(self):
        request = {"command": "get_public_info"}
        response = self.send_request(request)
        
        if response and response.get("status") == "success":
            data = response["data"]
            
            # Parse curve parameters
            p = int(data["p"], 16)
            a = int(data["a"], 16)
            b = int(data["b"], 16)
            
            # Tạo đường cong
            E = EllipticCurve(GF(p), [a, b])
            
            # Parse points
            base_x = int(data["base_point"]["x"], 16)
            base_y = int(data["base_point"]["y"], 16)
            P = E(base_x, base_y)
            
            pub_x = int(data["public_key"]["x"], 16)
            pub_y = int(data["public_key"]["y"], 16)
            Q = E(pub_x, pub_y)
            
            trace = data["trace_of_frobenius"]
            
            print(f"Curve parameters received:")
            print(f"  Order: {E.order()}")
            print(f"  Trace of Frobenius: {trace}")
            print(f"  Base point P: ({hex(int(P.xy()[0]))[:20]}..., {hex(int(P.xy()[1]))[:20]}...)")
            print(f"  Public key Q: ({hex(int(Q.xy()[0]))[:20]}..., {hex(int(Q.xy()[1]))[:20]}...)")
            print(f"  Vulnerable to Smart's Attack: {trace == 1}")
            
            return E, P, Q, trace
        else:
            print("Failed to get server info")
            if response:
                print(f"Server response: {response}")
            return None, None, None, None

    def lift_point(self, E, P, gf):
        """Lift a point to the p-adic field"""
        x, y = map(ZZ, P.xy())
        for point_ in E.lift_x(x, all=True):
            _, y_ = map(gf, point_.xy())
            if y == y_:
                return point_

    def smart_attack(self, G, P):
        print("\n=== STARTING SMART'S ATTACK ===")
        
        E = G.curve()
        gf = E.base_ring()
        p = gf.order()
        
        # Kiểm tra điều kiện
        trace = E.trace_of_frobenius()
        print(f"Trace of Frobenius: {trace}")
        
        if trace != 1:
            print("ERROR: Curve is not vulnerable to Smart's Attack!")
            return None
            
        print("✓ Curve is vulnerable (trace = 1)")
        
        try:
            # Tạo đường cong trên trường p-adic
            print("Lifting curve to p-adic field...")
            E_padic = EllipticCurve(Qp(p), [int(a) + p * ZZ.random_element(1, p) for a in E.a_invariants()])
            
            # Lift các điểm
            print("Lifting points to p-adic field...")
            G_lifted = p * self.lift_point(E_padic, G, gf)
            P_lifted = p * self.lift_point(E_padic, P, gf)
            
            # Tính logarithm
            print("Computing discrete logarithm...")
            Gx, Gy = G_lifted.xy()
            Px, Py = P_lifted.xy()
            
            result = int(gf((Px / Py) / (Gx / Gy)))
            
            print(f"✓ Private key found: {result}")
            
            # Verify
            if G * result == P:
                print("✓ Attack successful! Private key verified.")
                return result
            else:
                print("✗ Attack failed - verification error")
                return None
                
        except Exception as e:
            print(f"Attack error: {e}")
            return None

    def decrypt_with_key(self, encrypted_b64, key):
        """Giải mã dữ liệu bằng key"""
        try:
            encrypted_data = base64.b64decode(encrypted_b64)
            
            # Tạo AES key từ private key
            aes_key = sha1(str(key).encode()).digest()[:16]
            
            # Tách IV và ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Giải mã
            cipher = AES.new(aes_key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), 16)
            
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def run_demo(self):
        """Chạy demo tấn công"""
        if not self.connect():
            return
            
        try:
            print("=== PHASE 1: Getting server information ===")
            E, P, Q, trace = self.get_server_info()
            
            if not E:
                return
            print("\n=== PHASE 2: Performing Smart's Attack ===")
            private_key = self.smart_attack(P, Q)
            
            if not private_key:
                print("Attack failed!")
                return
            print("\n=== PHASE 3: Testing with server challenge ===")
            challenge_request = {"command": "challenge"}
            challenge_response = self.send_request(challenge_request)
            
            if challenge_response and challenge_response.get("status") == "success":
                encrypted_challenge = challenge_response["challenge"]
                print(f"Encrypted challenge received")
                decrypted = self.decrypt_with_key(encrypted_challenge, private_key)
                
                if decrypted:
                    print(f"✓ Challenge decrypted successfully!")
                    print(f"Decrypted message: {decrypted}")
                else:
                    print("✗ Failed to decrypt challenge")
            
            print(f"\n=== ATTACK SUMMARY ===")
            print(f"Target curve trace of Frobenius: {trace}")
            print(f"Private key recovered: {private_key}")
            print(f"Attack status: SUCCESS")
            
        except Exception as e:
            print(f"Demo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    print("Smart's Attack Demo - Client")
    print("Attacking ECC server with vulnerable curve...")
    print("-" * 50)
    
    client = SmartAttackClient()
    client.run_demo()
