from ecdsa import SigningKey, NIST256p
import socket
import json
import threading

class MyHash:
    def __init__(self, data):
        self.data = data
    
    def digest(self):
        return self.data  # LỖ HỔNG: không hash dữ liệu!

class VulnerableServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        
        # Tạo key pair cho server
        self.signing_key = SigningKey.generate(NIST256p)
        self.verifying_key = self.signing_key.verifying_key
        
        # Lưu trữ các giao dịch đã xử lý
        self.transactions = []
        
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"Server: {self.host}:{self.port}")
        print(f"Public key: {self.verifying_key.to_string().hex()}")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connected: {address}")
            
            client_thread = threading.Thread(
                target=self.handle_client, 
                args=(client_socket,)
            )
            client_thread.start()
    
    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                request = json.loads(data)
                response = self.process_request(request)
                
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            client_socket.close()
    
    def process_request(self, request):
        if request['action'] == 'get_public_key':
            return {
                'public_key': self.verifying_key.to_string().hex(),
                'status': 'success'
            }
            
        elif request['action'] == 'sign_transaction':
            message = request['message']
            signature = self.signing_key.sign(message.encode(), hashfunc=MyHash)
            
            transaction = {
                'message': message,
                'signature': signature.hex(),
                'timestamp': str(datetime.now())
            }
            self.transactions.append(transaction)
            
            return {
                'signature': signature.hex(),
                'status': 'success',
                'message': 'successfully signed transaction'
            }
            
        elif request['action'] == 'verify_transaction':
            message = request['message']
            signature_hex = request['signature']
            
            try:
                signature = bytes.fromhex(signature_hex)
                is_valid = self.verifying_key.verify(signature, message.encode(), hashfunc=MyHash)
                
                return {
                    'valid': True,
                    'status': 'success',
                    'message': 'valid signature',
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'status': 'error',
                    'message': f'unvalid signature: {str(e)}'
                }
        
        return {'status': 'error', 'message': 'Acrion not recognized'}

if __name__ == "__main__":
    from datetime import datetime
    server = VulnerableServer()
    server.start_server()