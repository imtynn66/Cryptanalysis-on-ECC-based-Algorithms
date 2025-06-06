from elliptic_curve import EllipticCurve, Point
from sage.all import random_prime

class Server:
    def __init__(self):
        # Chọn p lớn (ví dụ: số nguyên tố trong khoảng 2^31)
        self.p = random_prime(2**256, lbound=2**255)  # Một số nguyên tố lớn (Mersenne prime)
        # Đường cong CUSP y^2 = a2x^3 +a4x^2 + a6x + b
        a2 = 0
        a4 = 0
        a6 = 0
        self.curve = EllipticCurve( a2 , a4 , a6 , p=self.p)

        import random
        self.private_key = random.randint(1, self.p - 1)

        # Điểm G=(1,1) luôn hợp lệ cho y^2=x^3 trên mọi trường
        # Đảm bảo điểm G được biểu diễn dưới dạng phần tử của GF(p) khi truyền vào
        self.G = Point(1, 1, self.curve)

        self.public_key = self.curve.scalar_multiplication(self.private_key, self.G)
        print(f"\nServer Private Key: {self.private_key}")
        print(f"Server Public Key (P_server): {self.public_key.x}, {self.public_key.y}")

    def send_public_key_to_client(self):
        return {
            "curve_params": {
                "a2": self.curve.a2.lift(),
                "a4": self.curve.a4.lift(), 
                "a6": self.curve.a6.lift(),
                "p": self.curve.p
            },
            "base_point": {"x": self.G.x.lift(), "y": self.G.y.lift()},
            "server_public_key": {"x": self.public_key.x.lift(), "y": self.public_key.y.lift()}
        }

    def receive_client_public_key(self, client_public_key_data):
        client_Q = Point(client_public_key_data["x"], client_public_key_data["y"], self.curve)
        shared_secret_server = self.curve.scalar_multiplication(self.private_key, client_Q)
        print(f"\nServer tính toán khóa chung: {shared_secret_server.x}, {shared_secret_server.y}")
        return shared_secret_server

class Client:
    def __init__(self):
        self.curve = None
        self.G = None
        self.server_public_key_point = None
        self.private_key = None
        self.public_key = None

    def receive_server_info(self, server_data):
        params = server_data["curve_params"]
        self.curve = EllipticCurve(params["a2"], params["a4"], params["a6"], params["p"])
        self.G = Point(server_data["base_point"]["x"], server_data["base_point"]["y"], self.curve)
        self.server_public_key_point = Point(server_data["server_public_key"]["x"],
                                              server_data["server_public_key"]["y"], self.curve)
        print(f"Client nhận thông tin từ Server.")

    def generate_client_keys(self):
        import random
        self.private_key = random.randint(1, self.curve.p - 1)
        self.public_key = self.curve.scalar_multiplication(self.private_key, self.G)
        print(f"Client Private Key: {self.private_key}")
        print(f"Client Public Key: {self.public_key.x}, {self.public_key.y}")
        return {"x": self.public_key.x.lift(), "y": self.public_key.y.lift()}

    def calculate_shared_secret(self):
        shared_secret_client = self.curve.scalar_multiplication(self.private_key, self.server_public_key_point)
        print(f"Client tính toán khóa chung: {shared_secret_client.x}, {shared_secret_client.y}")
        return shared_secret_client

    def launch_attack(self, server_true_private_key):
        recovered_private_key = self.curve.attack_singular_curve(
            self.server_public_key_point,
            self.G
        )

        if recovered_private_key is not None:
            print("!!! TẤN CÔNG THÀNH CÔNG !!!")
            print(f"Khóa riêng của Server được suy ra: {recovered_private_key}")
            if recovered_private_key == server_true_private_key:
                print("Khóa riêng suy ra TRÙNG KHỚP với khóa riêng thực tế của Server.")
            else:
                print("Khóa riêng suy ra KHÔNG TRÙNG KHỚP (kiểm tra lại logic tấn công/demo).")
        else:
            print("Tấn công không thành công hoặc không thể suy ra khóa riêng.")


# --- Main Demo Cusp ---
if __name__ == "__main__":
    print("--- DEMO TẤN CÔNG ĐIỂM CUSP (SAGE) ---")
    server = Server()
    client = Client()

    server_info = server.send_public_key_to_client()
    client.receive_server_info(server_info)

    client_public_key_data = client.generate_client_keys()
    server.receive_client_public_key(client_public_key_data)

    _ = client.calculate_shared_secret() # Không cần lưu kết quả để tránh in lại 2 lần

    # Kẻ tấn công thực hiện tấn công
    client.launch_attack(server.private_key)