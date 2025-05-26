from sage.all import *
import socket
import threading
import json
import random
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

class ECCServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        
        # Curve params (vulnerable curve - trace of Frobenius = 1)
        self.p = 0xa15c4fb663a578d8b2496d3151a946119ee42695e18e13e90600192b1d0abdbb6f787f90c8d102ff88e284dd4526f5f6b6c980bf88f1d0490714b67e8a2a2b77
        self.a = 0x5e009506fcc7eff573bc960d88638fe25e76a9b6c7caeea072a27dcd1fa46abb15b7b6210cf90caba982893ee2779669bac06e267013486b22ff3e24abae2d42
        self.b = 0x2ce7d1ca4493b0977f088f6d30d9241f8048fdea112cc385b793bce953998caae680864a7d3aa437ea3ffd1441ca3fb352b0b710bb3f053e980e503be9a7fece
        
        self.E = EllipticCurve(GF(self.p), [self.a, self.b])
        self.P = self.E.gen(0)  # Base point
        
        print(f"Curve order: {self.E.order()}")
        print(f"Is prime order: {is_prime(self.E.order())}")
        print(f"Trace of Frobenius: {self.E.trace_of_frobenius()}")
        print(f"Vulnerable to Smart's Attack: {self.E.trace_of_frobenius() == 1}")
        
        self.private_key = random.randint(1, int(self.P.order()) - 1)
        self.public_key = self.P * self.private_key
        
        print(f"Server initialized with private key: {self.private_key}")
        print(f"Public key: {self.public_key}")

    def encrypt_message(self, message, shared_secret):
        """Mã hóa tin nhắn bằng shared secret"""
        key = sha1(str(shared_secret).encode()).digest()[:16]
        iv = random.randbytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        if isinstance(message, str):
            message = message.encode()
            
        encrypted = iv + cipher.encrypt(pad(message, 16))
        return base64.b64encode(encrypted).decode()

    def sage_to_json_safe(self, obj):
        """Convert SageMath objects to JSON-safe types"""
        if hasattr(obj, '__int__'):
            return int(obj)
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return obj

    def handle_client(self, client_socket, address):
        """Xử lý kết nối từ client"""
        print(f"New connection from {address}")
        
        try:
            while True:
                data = client_socket.recv(4096).decode()
                if not data:
                    break
                    
                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                    
                    # Convert response to JSON-safe format
                    json_response = json.dumps(response, default=self.sage_to_json_safe)
                    client_socket.send(json_response.encode())
                    
                except json.JSONDecodeError:
                    error_response = {"error": "Invalid JSON format"}
                    client_socket.send(json.dumps(error_response).encode())
                except Exception as e:
                    error_response = {"error": f"Server error: {str(e)}"}
                    client_socket.send(json.dumps(error_response).encode())
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection closed with {address}")

    def process_request(self, request):
        """Xử lý các yêu cầu từ client"""
        command = request.get("command")
        
        if command == "get_public_info":
            return {
                "status": "success",
                "data": {
                    "p": hex(int(self.p)),
                    "a": hex(int(self.a)), 
                    "b": hex(int(self.b)),
                    "base_point": {
                        "x": hex(int(self.P.xy()[0])),
                        "y": hex(int(self.P.xy()[1]))
                    },
                    "public_key": {
                        "x": hex(int(self.public_key.xy()[0])),
                        "y": hex(int(self.public_key.xy()[1]))
                    },
                    "curve_order": hex(int(self.E.order())),
                    "trace_of_frobenius": int(self.E.trace_of_frobenius())
                }
            }
            
        elif command == "encrypt":
            message = request.get("message", "Default secret message from server!")
            client_public_key_data = request.get("client_public_key")
            
            if client_public_key_data:
                # ECDH key exchange
                client_pub_x = int(client_public_key_data["x"], 16)
                client_pub_y = int(client_public_key_data["y"], 16)
                client_public_key = self.E(client_pub_x, client_pub_y)
                
                # Tính shared secret
                shared_point = client_public_key * self.private_key
                shared_secret = int(shared_point.xy()[0])  # Dùng x-coordinate làm shared secret
                
                encrypted_message = self.encrypt_message(message, shared_secret)
                
                return {
                    "status": "success",
                    "encrypted_message": encrypted_message,
                    "shared_secret_used": hex(shared_secret)  # Thông tin debug (không nên có trong thực tế)
                }
            else:
                return {"error": "Client public key required"}
                
        elif command == "challenge":
            # Tạo một challenge cho client
            challenge_message = "This is a secret flag: FLAG{sm4rt_4tt4ck_d3m0}"
            encrypted_challenge = self.encrypt_message(challenge_message, self.private_key)
            
            return {
                "status": "success", 
                "challenge": encrypted_challenge,
                "hint": "Decrypt this using the server's private key. Can you find it?"
            }
            
        else:
            return {"error": "Unknown command"}

    def start(self):
        """Khởi động server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")
            print("Waiting for connections...")
            
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = ECCServer()
    server.start()
