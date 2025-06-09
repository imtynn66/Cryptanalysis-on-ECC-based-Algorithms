from sage.all import GF, EllipticCurve
import random

# Anomalous curve parameters
a = 15347898055371580590890576721314318823207531963035637503096292
b = 7444386449934505970367865204569124728350661870959593404279615
p = 17676318486848893030961583018778670610489016512983351739677143
n = 0xFFFFFFFF  # Order of the curve (32-bit)

class Server:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
        self.curve = EllipticCurve(GF(p), [a, b])
        
        # Tìm điểm sinh G
        self.G = self._find_generator()
        print(f"Generator point G: {self.G}")
        
        # Tạo private key
        self.private_key = random.randint(1, n-1)
        print(f"Server private key: {self.private_key}")
        
        # Tính public key
        self.public_key = self.private_key * self.G
        print(f"Server public key: {self.public_key}")
    
    def _find_generator(self):
        """Tìm điểm sinh trên curve"""
        while True:
            x = GF(self.p).random_element()
            try:
                # Thử tìm điểm với x ngẫu nhiên
                point = self.curve.lift_x(x)
                # Kiểm tra điểm có phải sinh không
                if point.order() > 4:  # Tránh điểm bậc thấp
                    return point
            except:
                continue
    
    def get_public_params(self):
        """Trả về tham số public cho client"""
        return {
            'curve': self.curve,
            'G': self.G,
            'public_key': self.public_key
        }
    
    def compute_shared_secret(self, client_public_key):
        """Tính shared secret từ client public key"""
        self.shared_secret = self.private_key * client_public_key
        print(f"Server computed shared secret: {self.shared_secret}")
        return self.shared_secret

class Client:
    def __init__(self, server):
        params = server.get_public_params()
        self.curve = params['curve']
        self.G = params['G']
        self.server_public_key = params['public_key']
        
        # Tạo private key
        self.private_key = random.randint(1, n-1)
        print(f"Client private key: {self.private_key}")
        
        # Tính public key
        self.public_key = self.private_key * self.G
        print(f"Client public key: {self.public_key}")
    
    def compute_shared_secret(self):
        """Tính shared secret từ server public key"""
        self.shared_secret = self.private_key * self.server_public_key
        print(f"Client computed shared secret: {self.shared_secret}")
        return self.shared_secret

def demo_ecdh():
    """Demo quá trình trao đổi khóa ECDH"""
    print("\n=== DEMO ECDH KEY EXCHANGE ===")
    
    # Khởi tạo server
    server = Server(a, b, p)
    
    # Client nhận tham số từ server
    client = Client(server)
    
    # Server và client tính shared secret
    server_secret = server.compute_shared_secret(client.public_key)
    client_secret = client.compute_shared_secret()
    
    # Kiểm tra kết quả
    if server_secret == client_secret:
        print("\nECDH successful! Shared secrets match.")
        print(f"Shared secret: {server_secret}")
    else:
        print("\nError: Shared secrets do not match!")
    
    return server, client

if __name__ == "__main__":
    server, client = demo_ecdh()
        