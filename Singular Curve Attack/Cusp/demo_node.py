from elliptic_curve import EllipticCurve, Point
from sage.all import random_prime, GF

class Server:
    def __init__(self):
        self.p = 4368590184733545720227961182704359358435747188309319510520316493183539079703
                # Đường cong CUSP y^2 = a2x^3 +a4x^2 + a6x + b
        a2 = 1
        a4 = 0
        a6 = 0
        # y^2 = x^3 ==> cusp
        self.curve = EllipticCurve( a2 , a4 , a6 , self.p)

        F = GF(self.p)
        # base point
        gx = 8742397231329873984594235438374590234800923467289367269837473862487362482
        gy = 225987949353410341392975247044711665782695329311463646299187580326445253608
        self.G = Point(gx, gy, self.curve) 
        # public point
        px = 2582928974243465355371953056699793745022552378548418288211138499777818633265
        py = 2421683573446497972507172385881793260176370025964652384676141384239699096612

        self.public_key = Point(px, py, self.curve)
        self.private_key = 3963903911833444099026001790250531678485652182452420312170405092086735621359
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


# --- Main Demo Node ---
if __name__ == "__main__":
    print("--- DEMO TẤN CÔNG ĐIỂM NODE (SAGE) ---")
    server = Server()
    client = Client()

    server_info = server.send_public_key_to_client()
    client.receive_server_info(server_info)

    client_public_key_data = client.generate_client_keys()
    server.receive_client_public_key(client_public_key_data)

    _ = client.calculate_shared_secret() # Không cần lưu kết quả để tránh in lại 2 lần

    # Kẻ tấn công thực hiện tấn công
    client.launch_attack(server.private_key)
