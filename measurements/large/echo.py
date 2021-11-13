import socket

ip = "0.0.0.0"
port = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)

print("Starting echo server")

while(True):
    data, address = s.recvfrom(65535)
    INT = b""
    if len(data) >= 12:
        int_size = int(data[2]) * 4 #Third field of the INT shim header
        if len(data) > int_size:
            INT = data[0:int_size]
            response = data[int_size:].decode('utf-8')
        else:
            response = data.decode('utf-8')
    else:
        response = data.decode('utf-8')
    response = "echo: " + response
    s.sendto(INT+response.encode("utf-8"), address)