import socket
import json

class AttackerClient:
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
        print(f"Đã nhận public key: {self.public_key}")
    
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

# Demo tấn công
def attack_demo():
    legitimate_client = AttackerClient()
    legitimate_client.connect_to_server()
    original_message = "Please authorize a payment of $500 to Alice for consulting services."
    evil_message = "Please authorize a payment of $500 to Alice and $100,000 to Mallory's offshore account."
    
    print(f"Message: {original_message}")
    print(f"Evil Message: {evil_message}")
    
    example_signature = input("Stolen Signature: ")    
    try:
        is_valid_evil = legitimate_client.verify_transaction(evil_message, example_signature)
        
        if is_valid_evil:
            print("SUCCESS! The evil message was accepted by the server.")
        else:
            print("FAILED!")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    legitimate_client.close_connection()

if __name__ == "__main__":
    attack_demo()