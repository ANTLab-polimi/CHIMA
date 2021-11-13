import socket

def mpls_encode_type(type, value, tc, bos, ttl):
    val = 0
    label = (value & 0x3FFFF) | ((type & 0x3) << 18)
    val |= (label & 0xFFFFF) << 12
    val |= (tc & 0x7) << 9
    val |= (bos & 0x1) << 8
    val |= ttl
    return socket.htonl(val)
    
def mpls_encode(label, tc, bos, ttl):
    val = 0
    val |= (label & 0xFFFFF) << 12
    val |= (tc & 0x7) << 9
    val |= (bos & 0x1) << 8
    val |= ttl
    return socket.htonl(val)

class mpls_stack:
    def __init__(self):
        self.stack = []
        self.size = 0
    
    def add_label(self, value):
        self.stack.append(value)
        self.size += 1
    
    def __str__(self):
        result = ""
        for val in self.stack:
            result += "%s;" % hex(socket.ntohl(val))
        return result