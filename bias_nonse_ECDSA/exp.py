#!/usr/bin/env python3
from pwn import*
from sage.all import*
from Crypto.Util.number import *
from utilss import *
from sage.all import*
import random
from secrets import token_bytes
from msg import msg
proof.all(False)

def recvlineafter(io, lines):
    io.recvuntil(lines)
    rs = io.recvline()
    return rs


local = len(sys.argv) == 1
context.log_level = "debug"
file = "server.py"
io = process(["python", file]) if local else remote(sys.argv[1], int(sys.argv[2]))

xor = lambda a, b: bytes([x^y for x, y in zip(a, b)])

def sign_msg(msg):
    io.sendlineafter(b"> ", b"1")
    io.sendlineafter(b"in hex: ", msg.encode())
    # sig = recvlineafter(io, b"Here is your signature:").decode()
    io.recvuntil(b"Here is your signature:")
    sig = io.recvline().decode()
    return eval(sig)

def guess(guess):
    io.sendlineafter(b"> ", b"3")
    io.sendlineafter(b"Your guess >> ", guess)
    io.recvline()


hs = lambda x: hashlib.sha512(x).digest()
privkey = 5146830662633283467151605708506485847653084856753482980906171690925895263083806815569256084984501060354535416416387773244039804348156434744856506907315639731

def main():
    # while True:
    # sleep(0.5)
    # io = process(["python", file])
    # io=remote("",)
    pubkey = eval(io.recvline())
    P = pubkey
    # msg = [token_bytes(16) for _ in range(98)]
    # with open("msg.py", "w") as f:
    #     f.write("msg = "+str(msg))
    # print(P)
    p = 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff 
    a, b = 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc, 0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00
    n = 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409
    G = Coord(0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66, 0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650)
    ec_object = EC(a, b, p, n)
    dsa_object = DSA(ec_object, G)
    rs, ss, ms = [], [], []
    sigs = []
    for m in msg:
        sig = sign_msg(m.hex())
        r, s = sig
        rs.append(r)
        ss.append(s)
        ms.append(bytes_to_long(hs(m)))
        sigs.append((bytes_to_long(hs(m)), r, s))
        
    # assert len(sigs) == 91
    order = n
    B = 2**512
    M = matrix(QQ, len(ms)+2, len(ms)+2)

    # identity matrix [order, 0, 0] [0, order, 0 ] ..
    for i in range(len(ms)):
        M[i,i] = order        

    # calculations last two rows
    # t_n = r_n * s_n^-1
    # a_n = -(m_n * s_n^-1)
    for i in range(len(ms)):
        M[len(ms), i] = mod(rs[i] * inverse(ss[i], order), order) 
        M[len(ms)+1, i] = -mod(ms[i] * inverse(ss[i], order), order)  # <- minus a_i

    # last [B/order, 0] [0, B]
    M[len(ms), i+1] = QQ(B)/QQ(order)          # <- remember QQ
    M[len(ms)+1, len(ms)+1] = QQ(B)
    rows = M.LLL()
    for row in rows:    
        d = ((QQ(-(row[-2])) * order) / B) % order   
        # print(d)
        try:
            pub = ec_object.mul(G, d)
            # print(d)
            # print(pub, P)
            if str(P) == str(pub):
                print("[+] found privkey ", d)
                break
        except Exception as e:
            pass


    message = b'get flag'
    sig = dsa_object.sign(d, message)
    # print(sig)
    io.sendlineafter(b">", b"2")
    io.sendlineafter(b"r:", str(sig[0]))
    io.sendlineafter(b"s:", str(sig[1]))
    # io.interactive()
    flag = io.recvline()
    print(flag)
    # if b"Congratz!" in flag:
        # print(flag)
        # break
    # io.close()
    # W1{HNP_f0r_d4_v1Ct0l2Y_4ls0_Ch3ck_diss_0ut_CVE-2024-31497_2bba599fcfd02699561c9ad8c5f5ddbb}
if __name__ == '__main__':
    main()
