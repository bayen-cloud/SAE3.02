import random
from sympy import isprime

# ----------------------------------------------------
# Génération RSA simplifiée (librairies autorisées)
# ----------------------------------------------------

def generate_prime(bits=10):
    """
    Génère un petit nombre premier (10-12 bits) pour RSA simple.
    """
    while True:
        n = random.getrandbits(bits)
        if isprime(n):
            return n

def egcd(a, b):
    """Algorithme d’Euclide étendu pour inverse modulaire."""
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y

def modinv(a, m):
    """Inverse modulaire a^-1 mod m."""
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def generate_keys():
    """
    Génère une paire de clés RSA simple (public_key, private_key)
    Retourne (e, n), (d, n)
    """
    p = generate_prime(10)
    q = generate_prime(10)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    while phi % e == 0:
        e += 2

    d = modinv(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key

def encrypt(message_str, public_key):
    """
    Chiffre un message (string) → entier RSA
    """
    e, n = public_key
    m = int.from_bytes(message_str.encode(), "big")
    c = pow(m, e, n)
    return str(c)  # on renvoie une string (pas JSON)

def decrypt(cipher_str, private_key):
    """
    Déchiffre un entier RSA → string
    """
    d, n = private_key
    c = int(cipher_str)
    m = pow(c, d, n)
    msg = m.to_bytes((m.bit_length() + 7) // 8, "big")
    return msg.decode()
