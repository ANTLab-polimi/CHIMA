import socket

ip = "0.0.0.0"
port = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.settimeout(1)
print("Starting toupper server")

while(True):
    data, address = s.recvfrom(65535)
    INT = b""
    if len(data) >= 12:
        int_size = int(data[2]) * 4 #Third field of the INT shim header
        if len(data) > int_size:
            INT = data[0:int_size]
            up = data[int_size:].decode('utf-8').upper()
        else:
            up = data.decode('utf-8').upper()
    else:
        up = data.decode('utf-8').upper()

    #send to second function
    c.sendto(INT+up.encode('utf-8'), ("10.0.0.3", 12345))
    try:
        response, func_addr = c.recvfrom(65535)

        #reply to first function
        s.sendto(response, address)
    except socket.timeout as e:
        pass