
class Location():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
    def toString(self):
        return self.ip + ":" + str(self.port)
