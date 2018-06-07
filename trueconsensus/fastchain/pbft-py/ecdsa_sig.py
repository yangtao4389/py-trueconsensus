import os
import sys
import ecdsa
# import pickle

# from trueconsensus.fastchain.config import KD
import config

C = ecdsa.NIST256p
SIG_SIZE = 64
HASH_SIZE = 32

ASYMM_FILE_FORMATS = {
    "sign": ".pem",
    "verify": ".pub"
}


def generate_keys():
    sk = ecdsa.SigningKey.generate(curve=C)
    vk = sk.get_verifying_key()
    return sk, vk


def sign(key, message):
    return key.sign(message)


def verify(key, sig, message):
    try:
        rc = key.verify(sig, message)
        return rc
    except Exception as E:
        print(E)
        return False


def get_key_path(i, ktype):
    try:
        KEY_NAME = str(i) + ASYMM_FILE_FORMATS[ktype]
        print("KPATH - GET %s -- %s", ktype, KEY_NAME)
        return os.path.join(config.KD, ktype, KEY_NAME)
    except Exception as E:
        quit(E)
        raise


def write_new_keys(n):
    if not os.path.isdir(config.KD):
        os.mkdir(config.KD)
    for i in range(0, n):
        s_file = open(get_key_path(i, "sign"), 'wb')
        v_file = open(get_key_path(i, "verify"), 'wb')
        sk, vk = generate_keys()
        s_file.write(sk.to_pem())
        v_file.write(vk.to_pem())
    s_file.close()
    v_file.close()


def get_asymm_key(i, ktype=None):
    kpath = get_key_path(i, ktype)
    if not os.path.isfile(kpath):
        print("can't find key file: ", kpath)
        sys.exit(0)
    key_pem = open(kpath, 'rb').read()
    return ecdsa.SigningKey.from_pem(key_pem)

#
# def get_verifying_key(i):
#     kpath = get_key_path(i, "verify")
#     if not os.path.isfile(kpath):
#         print("can't find key file: ", kpath)
#         sys.exit(0)
#     key_pub = open(kpath, 'rb').read()
#     return ecdsa.VerifyingKey.from_pem(key_pem)


def read_keys_test(n, validate=False):
    if not os.path.isdir(config.KD):
        print("Can't find key directory")
        sys.exit(0)
    s = []
    v = []
    for i in range(0, n):
        secret_key = open(get_key_path(i, "sign"), "rb").read()
        public_key = open(get_key_path(i, "verify"), "rb").read()
        s.append(ecdsa.SigningKey.from_pem(secret_key))
        v.append(ecdsa.VerifyingKey.from_pem(public_key))
        if validate:
            assert validate_keypair(i, s[-1], v[-1]) is True
    return s, v


def validate_keypair(i, s, v):
    msg = "message" + str(i)
    sig = s.sign(msg)
    ver = v.verify(sig, msg)
    if not ver:
        print("Error while reading keypair: " % i)
        return False
    print("Round succeeded for keypair: " % i)
    return True


if __name__ == "__main__":
    N = int(sys.argv[1])
    write_new_keys(N)
    s, v = read_keys_test(N)
