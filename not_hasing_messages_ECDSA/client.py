import socket
import json

class LegitimateClient:
    def __init__(self, server_host='localhost', server_port=8080):
        self.server_host = server_host
        self.server_port = server_port
        self.public_key = None
    
    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))
        
        # Lấy public key từ server
        self.get_public_key()
    
    def send_request(self, request):
        self.socket.send(json.dumps(request).encode('utf-8'))
        response = self.socket.recv(4096).decode('utf-8')
        return json.loads(response)
    
    def get_public_key(self):
        request = {'action': 'get_public_key'}
        response = self.send_request(request)
        self.public_key = response['public_key']
        print(f"public_key: {self.public_key}")
    
    def sign_transaction(self, message):
        request = {
            'action': 'sign_transaction',
            'message': message
        }
        response = self.send_request(request)
        return response['signature']
    
    def verify_transaction(self, message, signature):
        request = {
            'action': 'verify_transaction',
            'message': message,
            'signature': signature
        }
        response = self.send_request(request)
        return response['valid']
    
    def close_connection(self):
        self.socket.close()

# Demo sử dụng client hợp pháp
def legitimate_demo():
    client = LegitimateClient()
    client.connect_to_server()
    
    # Giao dịch hợp pháp
    original_message = "Please authorize a payment of $500 to Alice for consulting services."
    print(f"Original Message: {original_message}")
    
    # Ký giao dịch
    signature = client.sign_transaction(original_message)
    print(f"Signature: {signature}")
    
    # Verify giao dịch gốc
    is_valid = client.verify_transaction(original_message, signature)
    print(f"VALID: {is_valid}")
    
    client.close_connection()

if __name__ == "__main__":
    legitimate_demo()