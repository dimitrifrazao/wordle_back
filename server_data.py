import os

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "static", "server_data.js")

class ServerData:

    LINES = ("var server_ip = '<HOST>';", "var server_port = '<PORT>';")

    @classmethod
    def createFile(cls, server_ip, server_port):
        f = open(file_path, 'w')
        f.write(cls.LINES[0].replace("<HOST>", server_ip))
        f.write(cls.LINES[1].replace("<PORT>", server_port))
        f.close()
