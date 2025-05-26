import gmpy2

# Curve parameters for secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __str__(self):
        if self == self.IDENTITY:
            return '<POINT AT INFINITY>'
        return f'({hex(self.x)}, {hex(self.y)})'
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __neg__(self):
        return Point(self.x, -self.y % P)

def point_add(P1, P2):
    if P1 == Point.IDENTITY:
        return P2
    if P2 == Point.IDENTITY:
        return P1
    
    if P1.x == P2.x:
        if P1.y == P2.y:
            # Point doubling
            if P1.y == 0:
                return Point.IDENTITY
            lam = (3 * P1.x * P1.x * pow(2 * P1.y, -1, P)) % P
        else:
            return Point.IDENTITY
    else:
        # Point addition
        lam = ((P2.y - P1.y) * pow(P2.x - P1.x, -1, P)) % P
    
    x3 = (lam * lam - P1.x - P2.x) % P
    y3 = (lam * (P1.x - x3) - P1.y) % P
    
    return Point(x3, y3)

def scalar_mult(k, P):
    if k == 0:
        return Point.IDENTITY
    elif k == 1:
        return P
    
    Q = Point.IDENTITY
    while k > 0:
        if k & 1:
            Q = point_add(Q, P)
        P = point_add(P, P)
        k >>= 1
    return Q

# Set class attributes
Point.IDENTITY = Point(0, 0)
G = Point(Gx, Gy) 