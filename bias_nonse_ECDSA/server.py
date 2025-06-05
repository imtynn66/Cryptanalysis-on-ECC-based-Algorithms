from utilss import *
import random


# FLAG = open("flag.txt", 'r').read()
FLAG = b"random_test_flag_here"
"""
NIST521p params
"""
p = 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff 
a, b = 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc, 0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00
n = 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409
G = Coord(0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66, 0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650)

ec_object = EC(a, b, p, n)
dsa_object = DSA(ec_object, G)

# privkey = 5146830662633283467151605708506485847653084856753482980906171690925895263083806815569256084984501060354535416416387773244039804348156434744856506907315639731

privkey = random.randrange(1, n)
pubkey = dsa_object.gen(privkey)

# print(privkey)
print(pubkey)


menu = """\
    [1] : Sign message
    [2] : Get flag
    [3] : Fun\
        """


GLOBAL_BANS = [b"Zeros", b"get flag"]


while True:
    try:    
        assert len(GLOBAL_BANS) <= 100, "I'm exhausted"
        print("Choose an option:")
        print(menu)
        
        opt = int(input("> "))

        if opt == 1:
            message = input("Give me da message in hex: ")
            try:
                message = bytes.fromhex(message)
                assert message not in GLOBAL_BANS
                GLOBAL_BANS.append(message)
            except:
                print("no hack plis")
                exit()
            sig = dsa_object.sign(privkey, message)
            print("Here is your signature:", sig)
            continue
        elif opt == 2:
            print("Rizz me with signature of 'get flag' and you shall pass")
            r = int(input("r: "))
            s = int(input("s: "))
            if dsa_object.validate(pubkey, b'get flag', (r, s)):
                print("Congratz! Here is your reward", FLAG)
                exit()
            else:
                print("skill issue...")
                exit()
        elif opt == 3:
            print("Welcome to my supa sigma secret. If you manage to guess the right number, skibidi reward for u <3")
            sec = random.randint(1, 20)
            num = int(input("Your guess >> "))
            if num == sec:
                print("Get fun")
            continue
        else:
            print("wut da heo :((")
            exit()
    except Exception as e:
        print(f"Error: {e}")
        exit()