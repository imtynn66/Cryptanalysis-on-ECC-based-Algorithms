#!/usr/bin/python3 
from elliptic_curve import Curve, Point
from Crypto.Util.number import bytes_to_long
import os
from random import *
from secrets import randbelow
from Crypto.Cipher import ARC4

flag = b"i_love_crypto"

# NIST P-256
a = -3
b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
E = Curve(p, a, b)
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
G = Point(E, Gx, Gy)

# server's secret
d = randint(1, n-1)
P = G * d


def encryptFlag(P, m):
    key = point_to_bytes(P)
    return ARC4.new(key).encrypt(m)

def point_to_bytes(P):
    return P.x.to_bytes(32, "big") + P.y.to_bytes(32, "big")


print(f"Public key: {P}")

while True:
    try:
        print("1. Start a Diffie-Hellman key exchange")
        print("2. Get an encrypted flag")
        print("3. Exit")
        option = int(input("> "))
        if option == 1:
            print("Send public key pleased:")
            x = int(input("x: "))
            y = int(input("y: "))
            S = Point(E, x, y) * d
            print(S)
        elif option == 2:
            r = randbelow(n)
            C1 = r * G
            C2 = encryptFlag(r * P, flag)
            
            with open("flag.enc", "wb") as fi:
                fi.write(C2)
            fi.close()
            print(point_to_bytes(C1).hex())
        elif option == 3:
            break
        print()
    except Exception as error:
        print(error)
        break