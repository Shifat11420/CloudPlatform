
class Location():
    def __init__(self, ip, port, location):
        self.ip = ip
        self.port = int(port)
        self.location = location
    def toString(self):
        return self.ip + ":" + str(self.port)+":" + str(self.location)
