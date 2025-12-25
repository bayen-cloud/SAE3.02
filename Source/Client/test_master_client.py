import socket

MASTER_IP = "127.0.0.1"
MASTER_CLIENT_PORT = 6000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((MASTER_IP, MASTER_CLIENT_PORT))
data = s.recv(8192).decode()
s.close()

print("=== DONNÉES BRUTES REÇUES DU MASTER ===")
print(data)
