#!/usr/bin/env python3
"""
ECDSA Nonce Reuse Attack Simulation
Mô phỏng tấn công sử dụng lại nonce trong chữ ký số ECDSA
"""

import hashlib
import secrets
import socket
import threading
import time
import json
from typing import Tuple, List, Optional

# Sử dụng thư viện tinyec để thực hiện ECDSA đơn giản
# Trong thực tế nên dùng cryptography library
class SimpleECDSA:
    def __init__(self):
        # Sử dụng curve secp256k1 (giống Bitcoin)
        self.p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        self.a = 0
        self.b = 7
        self.Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        self.Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        
    def mod_inverse(self, a: int, m: int) -> int:
        """Tính nghịch đảo modular"""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m
    
    def point_add(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
        """Cộng hai điểm trên elliptic curve"""
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        
        x1, y1 = p1
        x2, y2 = p2
        
        if x1 == x2:
            if y1 == y2:
                # Point doubling
                s = (3 * x1 * x1 + self.a) * self.mod_inverse(2 * y1, self.p) % self.p
            else:
                return None  # Point at infinity
        else:
            s = (y2 - y1) * self.mod_inverse(x2 - x1, self.p) % self.p
        
        x3 = (s * s - x1 - x2) % self.p
        y3 = (s * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def point_multiply(self, k: int, point: Tuple[int, int]) -> Tuple[int, int]:
        """Nhân vô hướng điểm với số nguyên k"""
        if k == 0:
            return None
        if k == 1:
            return point
        
        result = None
        addend = point
        
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)
            k >>= 1
        
        return result
    
    def generate_keypair(self) -> Tuple[int, Tuple[int, int]]:
        """Tạo cặp khóa ECDSA"""
        private_key = secrets.randbelow(self.n - 1) + 1
        public_key = self.point_multiply(private_key, (self.Gx, self.Gy))
        return private_key, public_key
    
    def hash_message(self, message: str) -> int:
        """Hash message thành số nguyên"""
        h = hashlib.sha256(message.encode()).digest()
        return int.from_bytes(h, 'big') % self.n
    
    def sign_with_nonce(self, message: str, private_key: int, nonce: int) -> Tuple[int, int]:
        """Ký message với nonce cụ thể (KHÔNG AN TOÀN - chỉ để demo)"""
        z = self.hash_message(message)
        
        # Tính r = (k * G).x mod n
        point = self.point_multiply(nonce, (self.Gx, self.Gy))
        r = point[0] % self.n
        
        if r == 0:
            raise ValueError("Invalid nonce")
        
        # Tính s = k^(-1) * (z + r * private_key) mod n
        k_inv = self.mod_inverse(nonce, self.n)
        s = (k_inv * (z + r * private_key)) % self.n
        
        if s == 0:
            raise ValueError("Invalid signature")
        
        return r, s
    
    def sign(self, message: str, private_key: int) -> Tuple[int, int]:
        """Ký message với nonce ngẫu nhiên (AN TOÀN)"""
        while True:
            nonce = secrets.randbelow(self.n - 1) + 1
            try:
                return self.sign_with_nonce(message, private_key, nonce)
            except ValueError:
                continue
    
    def verify(self, message: str, signature: Tuple[int, int], public_key: Tuple[int, int]) -> bool:
        """Xác thực chữ ký"""
        r, s = signature
        if not (1 <= r < self.n and 1 <= s < self.n):
            return False
        
        z = self.hash_message(message)
        
        try:
            s_inv = self.mod_inverse(s, self.n)
            u1 = (z * s_inv) % self.n
            u2 = (r * s_inv) % self.n
            
            point1 = self.point_multiply(u1, (self.Gx, self.Gy))
            point2 = self.point_multiply(u2, public_key)
            point = self.point_add(point1, point2)
            
            if point is None:
                return False
            
            return (point[0] % self.n) == r
        except:
            return False

def solve_congruence(a: int, b: int, n: int) -> List[int]:
    """Giải phương trình ax ≡ b (mod n)"""
    def gcd_extended(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = gcd_extended(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = gcd_extended(a % n, n)
    
    if b % gcd != 0:
        return []
    
    x = (x * (b // gcd)) % n
    solutions = []
    
    for i in range(gcd):
        solutions.append((x + i * (n // gcd)) % n)
    
    return solutions

def nonce_reuse_attack(n: int, m1: int, r1: int, s1: int, m2: int, r2: int, s2: int) -> List[Tuple[int, int]]:
    """
    Tấn công nonce reuse để khôi phục private key
    """
    results = []
    
    # Nếu r1 == r2, có thể nonce đã bị reuse
    if r1 == r2:
        # k = (m1 - m2) / (s1 - s2) mod n
        for k in solve_congruence(int(s1 - s2), int(m1 - m2), int(n)):
            # private_key = (s*k - m) / r mod n
            for x in solve_congruence(int(r1), int(k * s1 - m1), int(n)):
                results.append((int(k), int(x)))
    
    return results

class VulnerableServer:
    """Server có lỗ hổng nonce reuse"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.ecdsa = SimpleECDSA()
        self.private_key, self.public_key = self.ecdsa.generate_keypair()
        self.vulnerable_nonce = None  # Nonce sẽ bị reuse
        self.signatures = []  # Lưu trữ signatures để attacker phân tích
        
        print(f"[SERVER] Private key: {hex(self.private_key)}")
        print(f"[SERVER] Public key: ({hex(self.public_key[0])}, {hex(self.public_key[1])})")
    
    def handle_client(self, conn, addr):
        """Xử lý request từ client"""
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                request = json.loads(data)
                
                if request['action'] == 'get_public_key':
                    response = {
                        'public_key': {
                            'x': hex(self.public_key[0]),
                            'y': hex(self.public_key[1])
                        }
                    }
                    
                elif request['action'] == 'sign':
                    message = request['message']
                    
                    # LỖ HỔNG: Reuse nonce cho 2 message đầu tiên
                    if len(self.signatures) == 0:
                        # Tạo nonce vulnerable cho lần đầu
                        self.vulnerable_nonce = secrets.randbelow(self.ecdsa.n - 1) + 1
                        r, s = self.ecdsa.sign_with_nonce(message, self.private_key, self.vulnerable_nonce)
                        print(f"[SERVER] VULNERABLE: Using nonce {hex(self.vulnerable_nonce)} for message 1")
                    elif len(self.signatures) == 1:
                        # Reuse nonce cho message thứ 2 (LỖ HỔNG!)
                        r, s = self.ecdsa.sign_with_nonce(message, self.private_key, self.vulnerable_nonce)
                        print(f"[SERVER] VULNERABLE: Reusing nonce {hex(self.vulnerable_nonce)} for message 2!")
                    else:
                        # Từ message thứ 3 trở đi dùng nonce ngẫu nhiên
                        r, s = self.ecdsa.sign(message, self.private_key)
                        print(f"[SERVER] SAFE: Using random nonce for message {len(self.signatures) + 1}")
                    
                    signature_data = {
                        'message': message,
                        'r': hex(r),
                        's': hex(s),
                        'message_hash': hex(self.ecdsa.hash_message(message))
                    }
                    
                    self.signatures.append(signature_data)
                    
                    response = {
                        'signature': signature_data,
                        'message_count': len(self.signatures)
                    }
                    
                elif request['action'] == 'get_signatures':
                    response = {
                        'signatures': self.signatures,
                        'curve_order': hex(self.ecdsa.n)
                    }
                
                conn.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"[SERVER] Error handling client {addr}: {e}")
        finally:
            conn.close()
    
    def start(self):
        """Khởi động server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            print(f"[SERVER] Vulnerable ECDSA server started on {self.host}:{self.port}")
            
            while True:
                conn, addr = server_socket.accept()
                print(f"[SERVER] New connection from {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()

class AttackerClient:
    """Client thực hiện tấn công nonce reuse"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.ecdsa = SimpleECDSA()
    
    def connect_and_attack(self):
        """Kết nối tới server và thực hiện tấn công"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                
                # 1. Lấy public key
                print("\n[ATTACKER] Step 1: Getting server's public key...")
                request = {'action': 'get_public_key'}
                sock.send(json.dumps(request).encode())
                response = json.loads(sock.recv(1024).decode())
                
                server_public_key = (
                    int(response['public_key']['x'], 16),
                    int(response['public_key']['y'], 16)
                )
                print(f"[ATTACKER] Server public key: ({hex(server_public_key[0])}, {hex(server_public_key[1])})")
                
                # 2. Yêu cầu server ký 2 messages khác nhau
                print("\n[ATTACKER] Step 2: Requesting signatures for different messages...")
                
                messages = ["Hello World", "Attack Message"]
                
                for i, message in enumerate(messages):
                    request = {'action': 'sign', 'message': message}
                    sock.send(json.dumps(request).encode())
                    response = json.loads(sock.recv(1024).decode())
                    print(f"[ATTACKER] Got signature {i+1} for message: '{message}'")
                    print(f"[ATTACKER] r: {response['signature']['r']}")
                    print(f"[ATTACKER] s: {response['signature']['s']}")
                
                # 3. Lấy tất cả signatures để phân tích
                print("\n[ATTACKER] Step 3: Analyzing signatures for nonce reuse...")
                request = {'action': 'get_signatures'}
                sock.send(json.dumps(request).encode())
                response = json.loads(sock.recv(1024).decode())
                
                signatures = response['signatures']
                curve_order = int(response['curve_order'], 16)
                
                # 4. Kiểm tra nonce reuse và tấn công
                if len(signatures) >= 2:
                    sig1 = signatures[0]
                    sig2 = signatures[1]
                    
                    r1 = int(sig1['r'], 16)
                    s1 = int(sig1['s'], 16)
                    m1 = int(sig1['message_hash'], 16)
                    
                    r2 = int(sig2['r'], 16)
                    s2 = int(sig2['s'], 16)
                    m2 = int(sig2['message_hash'], 16)
                    
                    print(f"[ATTACKER] Signature 1: r={hex(r1)}, s={hex(s1)}")
                    print(f"[ATTACKER] Signature 2: r={hex(r2)}, s={hex(s2)}")
                    
                    if r1 == r2:
                        print("\n[ATTACKER]  NONCE REUSE DETECTED! ")
                        print("[ATTACKER] r1 == r2, attempting to recover private key...")
                        
                        # Thực hiện tấn công
                        results = nonce_reuse_attack(curve_order, m1, r1, s1, m2, r2, s2)
                        
                        for nonce, private_key in results:
                            print(f"\n[ATTACKER]  RECOVERED:")
                            print(f"[ATTACKER] Nonce: {hex(nonce)}")
                            print(f"[ATTACKER] Private Key: {hex(private_key)}")
                            
                            # Verify private key
                            recovered_public = self.ecdsa.point_multiply(private_key, (self.ecdsa.Gx, self.ecdsa.Gy))
                            if recovered_public == server_public_key:
                                print("[ATTACKER]  PRIVATE KEY RECOVERY SUCCESSFUL!")
                                print("[ATTACKER]   Server's private key has been compromised!")
                                
                                # Demonstrate attack by forging a signature
                                fake_message = "I am the server"
                                fake_sig = self.ecdsa.sign(fake_message, private_key)
                                
                                if self.ecdsa.verify(fake_message, fake_sig, server_public_key):
                                    print(f"[ATTACKER]  Successfully forged signature for: '{fake_message}'")
                                    print(f"[ATTACKER] Forged signature: r={hex(fake_sig[0])}, s={hex(fake_sig[1])}")
                                
                                return True
                            else:
                                print("[ATTACKER]  Private key verification failed")
                    else:
                        print("[ATTACKER] No nonce reuse detected (r1 != r2)")
                
                return False
                
        except Exception as e:
            print(f"[ATTACKER] Error: {e}")
            return False

def main():
    """Demo chính"""
    print("="*60)
    print("ECDSA NONCE REUSE ATTACK DEMONSTRATION")
    print("Mô phỏng tấn công sử dụng lại nonce trong ECDSA")
    print("="*60)
    
    # Khởi động server trong thread riêng
    server = VulnerableServer()
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Đợi server khởi động
    time.sleep(1)
    
    # Thực hiện tấn công
    attacker = AttackerClient()
    success = attacker.connect_and_attack()
    
    if success:
        print("\n" + "="*60)
        print(" ATTACK SUCCESSFUL!")
        print("Lỗ hổng nonce reuse đã được khai thác thành công.")
        print("Private key của server đã bị lộ!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print(" Attack failed or no vulnerability found")
        print("="*60)

if __name__ == "__main__":
    main()