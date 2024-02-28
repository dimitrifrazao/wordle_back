import os

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "static", "server_data.js")

class ServerData:

    LINE = '''window.REACT_APP_API_URL="<IP>:<PORT>";'''

    @classmethod
    def createFile(cls, server_ip, server_port):
        line = cls.LINE.replace("<IP>", server_ip).replace("<PORT>", server_port)
        print('server data: ', line)
        f = open(file_path, 'w')
        f.write(line)
        f.close()
