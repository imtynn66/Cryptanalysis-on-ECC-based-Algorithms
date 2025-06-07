# elliptic_curve.py
from sage.all import GF, discrete_log, power_mod

# --- Lớp Point ---
class Point:
    def __init__(self, x, y, curve):
        self.x = GF(curve.p)(x) if x is not None else None
        self.y = GF(curve.p)(y) if y is not None else None
        self.curve = curve

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.curve == other.curve

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.x is None and self.y is None:
            return "Point at Infinity (O)"
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()

# --- Lớp EllipticCurve ---
class EllipticCurve:
    def __init__(self, a, b , c , p):
        self.p = p
        # Các tham số a2, a4, a6 của đường cong y^2 = x^3 + a2*x^2 + a4*x + a6
        self.a2 = GF(p)(a) if a is not None else GF(p)(0) 
        self.a4 = GF(p)(b) if b is not None else GF(p)(0)  # A in y^2 = x^3 + Ax + B form if a2=0
        self.a6 = GF(p)(c) if c is not None else GF(p)(0)  # B in y^2 = x^3 + Ax + B form if a2=0
        
        self.O = Point(None, None, self) # Point at infinity
        discriminant_simplified = (4 * self.a4**3 + 27 * self.a6**2) 
        
        if discriminant_simplified.is_zero():
            R = GF(self.p)['x']
            x_poly = R.gen()
            # Define the polynomial f(x) = x^3 + a2*x^2 + a4*x + a6
            f_poly = x_poly**3 + self.a2 * x_poly**2 + self.a4 * x_poly + self.a6
            roots_with_multiplicities = f_poly.roots()
            print(f"Phươn trình : y^2 = x^3 + {self.a2}x^2 + {self.a4}x + {self.a6} (mod {self.p}) có điểm kỳ dị (Singular Point).")
            if len(roots_with_multiplicities) == 1 and roots_with_multiplicities[0][1] == 3:
                print(f"  --> Đây là CUSP tại ({roots_with_multiplicities[0][0]}, 0).")
            elif len(roots_with_multiplicities) > 0 and any(root[1] >= 2 for root in roots_with_multiplicities):
                print(f"  --> Đây là NODE hoặc CUSP (nghiệm bội).")
                # More precise check for Node vs Cusp based on derivative
                singular_points = []
                f_prime = f_poly.derivative()
                for root, mult in roots_with_multiplicities:
                    if f_prime(root) == 0: # Check if it's a singular point
                        singular_points.append(root)
                
                if len(singular_points) == 1 and f_poly(singular_points[0]) == 0 and f_poly.derivative(1)(singular_points[0]) == 0 and f_poly.derivative(2)(singular_points[0]) != 0:
                     print(f"  --> Đây là NODE tại ({singular_points[0]}, 0).")
                elif len(singular_points) == 1 and f_poly(singular_points[0]) == 0 and f_poly.derivative(1)(singular_points[0]) == 0 and f_poly.derivative(2)(singular_points[0]) == 0:
                     print(f"  --> Đây là CUSP tại ({singular_points[0]}, 0).")
                else:
                    print("  --> Loại kỳ dị không xác định rõ (có thể là Node hoặc Cusp tùy trường hợp).")

            else:
                print("  --> Loại kỳ dị không xác định rõ (có thể là Node hoặc Cusp tùy trường hợp).")
        else:
            print(f"Đường cong y^2 = x^3 + {self.a2}x^2 + {self.a4}x + {self.a6} (mod {self.p}) là đường cong KHÔNG KỲ DỊ (Non-singular Curve).")
            
    def is_on_curve(self, x, y):
        if x is None and y is None: # Point at infinity
            return True
        # Ensure x and y are GF(p) elements for consistent arithmetic
        x_gf = GF(self.p)(x)
        y_gf = GF(self.p)(y)
        # Check against the general Weierstrass equation
        return (y_gf**2) == (x_gf**3 + self.a2 * x_gf**2 + self.a4 * x_gf + self.a6)

    def point_addition(self, P1, P2):
        if P1 == self.O:
            return P2
        if P2 == self.O:
            return P1        
        if P1.x == P2.x:
            if P1.y != P2.y: # P1 = -P2
                return self.O
            else: # P1 = P2 (Point Doubling)
                if P1.y == GF(self.p)(0): # Tangent is vertical (y=0), result is O
                    return self.O
                # Slope for point doubling on y^2 = x^3 + a2*x^2 + a4*x + a6
                # dy/dx of y^2 = x^3 + a2*x^2 + a4*x + a6 is 2y dy/dx = 3x^2 + 2a2*x + a4
                # So, dy/dx = (3x^2 + 2a2*x + a4) / (2y)
                slope = (3 * P1.x**2 + 2 * self.a2 * P1.x + self.a4) / (2 * P1.y) 
        else: # P1 != P2 (Point Addition)
            slope = (P2.y - P1.y) / (P2.x - P1.x)

        x3 = slope**2 - P1.x - P2.x - self.a2
        y3 = slope * (P1.x - x3) - P1.y - self.a2 * x3 # Adjust y3 for a2x^2 term
        return Point(x3, y3, self)

    def scalar_multiplication(self, k, P):
        if k == 0:
            return self.O
        result = self.O
        addend = P
        # Binary method for scalar multiplication
        while k > 0:
            if k % 2 == 1:
                result = self.point_addition(result, addend)
            addend = self.point_addition(addend, addend)
            k //= 2
        return result

    # --- Hàm tấn công cho Cusp ---
    def attack_cusp_method(self, Gx, Gy, Px, Py):
        print("\n--- Bắt đầu tấn công CUSP ---")
        R = GF(self.p)['x']
        x = R.gen()
        # Define f(x) based on current curve parameters (a2, a4, a6)
        f = x**3 + self.a2 * x**2 + self.a4 * x + self.a6
        print(f"1. Xác định đa thức f(x) = x^3 + {self.a2}x^2 + {self.a4}x + {self.a6}")

        roots = f.roots()
        print(f"2. Tìm nghiệm của f(x): {roots}")

        Gx_gf = GF(self.p)(Gx)
        Gy_gf = GF(self.p)(Gy)
        Px_gf = GF(self.p)(Px)
        Py_gf = GF(self.p)(Py)
        print(f"Điểm cơ sở G: ({Gx_gf}, {Gy_gf})")
        print(f"Khóa công khai P_server: ({Px_gf}, {Py_gf})")
        
        if len(roots) == 1 and roots[0][1] == 3: # Cusp has a single root with multiplicity 3
            alpha = roots[0][0] # Alpha is the x-coordinate of the Cusp
            print(f"3. Xác định Cusp tại x = alpha = {alpha} (vì có nghiệm bội 3).")
            
            # Map G and P_server to the additive group Z_p
            # This mapping is specific to the cusp at (alpha, 0)
            print("4. Ánh xạ các điểm vào nhóm cộng tính Z_p (ánh xạ phi(x,y) = (x - alpha) / y)")
            u = (Gx_gf - alpha) / Gy_gf
            print(f"   Tính u = phi(G) = ({Gx_gf} - {alpha}) / {Gy_gf} = {u}")
            v = (Px_gf - alpha) / Py_gf
            print(f"   Tính v = phi(P_server) = ({Px_gf} - {alpha}) / {Py_gf} = {v}")
            
            # Solve DLP in the additive group: v = k * u => k = v / u
            recovered_private_key = int(v / u)
            print(f"5. Giải bài toán Logarit Rời rạc trong nhóm cộng tính: v = k * u => k = v / u")
            print(f"   Khóa riêng k = {v} / {u} = {recovered_private_key}")
            return recovered_private_key
        else:
            print("Đường cong không phải CUSP với nghiệm bội 3, không thể áp dụng tấn công này.")
            return None

    # --- Hàm tấn công cho Node ---
    def attack_node_method(self, Gx, Gy, Px, Py):
        R = GF(self.p)['x']
        x = R.gen()
        f = x**3 + self.a2 * x**2 + self.a4 * x + self.a6
        roots_with_multiplicities = f.roots()
        len_roots = len(roots_with_multiplicities)
        alpha = None
        beta = None
        if len(roots_with_multiplicities) == 2:
            # Tìm double root và simple root
            if roots_with_multiplicities[0][1] == 2:
                alpha = roots_with_multiplicities[0][0]  # Double root
                beta = roots_with_multiplicities[1][0]   # Simple root
            elif roots_with_multiplicities[1][1] == 2:
                alpha = roots_with_multiplicities[1][0]  # Double root
                beta = roots_with_multiplicities[0][0]   # Simple root
            else:
                print("Curve is not a node with double root, cannot apply this attack.")
                return None    
            print(f"Double root: α = {alpha}")
            print(f"Simple root: β = {beta}")           
            try:
                # Tính tham số biến đổi
                t = (alpha - beta).sqrt()
                print(f"Parameter t = √(α - β) = {t}")
                
                # Kiểm tra các trường hợp đặc biệt
                if Gx == alpha or Px == alpha:
                    print("Points lie on vertical line x = α, cannot apply this method")
                    return None
                u = (Gy + t * (Gx - alpha)) / (Gy - t * (Gx - alpha))
                v = (Py + t * (Px - alpha)) / (Py - t * (Px - alpha))
                
                print(f"u = (G.y + t(G.x - α))/(G.y - t(G.x - α)) = {u}")
                print(f"v = (P.y + t(P.x - α))/(P.y - t(P.x - α)) = {v}")
                # Tính discrete log trong multiplicative group
                try:
                    #k = int(v.log(u)) 
                    k = int(discrete_log(v, u))
                    print(f"Private key found: k = {k}")
                    return k
                except ValueError as e:
                    print(f"Error in discrete log calculation: {e}")
                    return None
                
            except Exception as e:
                print(f"Error in node attack: {e}")
                return None
        else:
            print("Curve is not a node with double root, cannot apply this attack.")
            return None
        
        
    def attack_singular_curve(self, server_public_key_point, G):
        print("\n  Đang thực hiện tấn công bằng phương pháp ánh xạ vào nhóm con...")
        R = GF(self.p)['x']
        x_poly = R.gen()
        f_poly = x_poly**3 + self.a2 * x_poly**2 + self.a4 * x_poly + self.a6
        roots_with_multiplicities = f_poly.roots()

        # Check for Cusp (triple root)
        if len(roots_with_multiplicities) == 1 and roots_with_multiplicities[0][1] == 3:
            print("  --> Phát hiện CUSP. Áp dụng tấn công Cusp.")
            return self.attack_cusp_method(G.x, G.y, server_public_key_point.x, server_public_key_point.y)
        # Check for Node (double root)
        elif len(roots_with_multiplicities) > 0 and any(root[1] >= 2 for root in roots_with_multiplicities):
            # A more precise check for a node is needed if there are more than two roots.
            # For simplicity, here we're checking for any root with multiplicity >= 2.
            # A true node has one root with multiplicity 2 and another with multiplicity 1.
            print("  --> Phát hiện NODE. Áp dụng tấn công Node.")
            return self.attack_node_method(G.x, G.y, server_public_key_point.x, server_public_key_point.y)
        else:
            print("  --> Không xác định được loại điểm kỳ dị (Node/Cusp) rõ ràng. Không thể áp dụng tấn công cụ thể.")
            return None

def find_valid_point(curve, field):
    for x_int in range(2, 100):
        x = field(x_int)
        rhs = x**2 * (x + 1)
        if rhs.is_square():
            y = rhs.sqrt()
            P = Point(x, y, curve)
            # Tránh điểm kỳ dị và điểm có hoành độ hoặc tung độ bằng 0
            if x != 0 and y != 0:
                return P
    raise ValueError("Không tìm thấy điểm phù hợp.")