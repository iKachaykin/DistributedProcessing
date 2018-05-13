from multiprocessing import Process
import socket
import numpy as np


class StandardTaskWorker(Process):

    def __init__(self, address, size_of_signal, encoding='utf-8', delim=',', end_str=';', res_delim='|', name='Worker',
                 result_type=int, mpath='/users/ivankachaikin/PycharmProjects/ProjectFiles/Matrix/',
                 vpath='/users/ivankachaikin/PycharmProjects/ProjectFiles/Vector/'):
        super().__init__(target=self.target)
        self.encoding = encoding
        self.sock = socket.socket()
        self.sock.setblocking(0)
        self.address = address
        self.size_of_signal = size_of_signal
        self.delim = delim
        self.end_str = end_str
        self.res_delim = res_delim
        self.name = name
        self.result_type = result_type
        self.mpath = mpath
        self.vpath = vpath
        self.rindex = -1

    def target(self):
        # print('Worker "%s" is starting to work' % self.name)
        while True:
            try:
                self.sock.connect(self.address)
            except socket.error as err:
                if err.errno == 56:
                    # print('Worker "%s": connection between host and me was accepted' % self.name)
                    break
            else:
                # print('Worker "%s": connection between host and me was accepted' % self.name)
                break
        data = ""
        while not (self.end_str in data):
            try:
                tmp_data = self.sock.recv(self.size_of_signal)
            except socket.error as err:
                pass
            else:
                data += tmp_data.decode(self.encoding)
        rinds = data.replace(self.end_str, '').split(self.delim)
        rinds = rinds[:len(rinds) - 1]
        # print('Worker "{0}": data from host: {1}'.format(self.name, rinds))
        for rindex in rinds:
            self.rindex = int(rindex)
            value = self.multiplication()
            data = "{0}{1}{2}{3}".format(rindex, self.delim, value, self.res_delim)
            self.sock.send(data.encode(self.encoding))
        self.sock.close()

    def multiplication(self):
        mfile = open(self.mpath + 'm%d.txt' % self.rindex, 'r')
        buf = mfile.read().split(' ')
        mfile.close()
        buf = buf[:len(buf) - 1]
        row = np.array(buf, dtype=int)
        vfile = open(self.vpath + 'v0.txt', 'r')
        buf = vfile.read().split(' ')
        vfile.close()
        buf = buf[:len(buf) - 1]
        vector = np.array(buf, dtype=int)
        return np.dot(row, vector)
