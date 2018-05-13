import os
import sys
from socket import error as socket_error
from socket import socket
from numpy.random import randint
from multiprocessing import Process


class StandardTaskClient(Process):

    def __init__(self, name, address, path, row_num, col_num, matrix_create_mode='unit', vector_create_mode='random',
                 encoding='utf-8', delim=',', end_str=';'):
        if row_num * col_num > 1e+10:
            raise OverflowError('Too much data!')
        try:
            int(delim), int(end_str)
        except:
            pass
        else:
            raise ValueError('\"delim\" and \"end_str\" arguments could not be integers!')
        super().__init__(target=self.target)
        self.name = name
        self.address = address
        self.sock = socket()
        self.sock.setblocking(0)
        self.path = path
        self.directory = path + name + '/'
        if delim in self.directory or end_str in self.directory:
            raise ValueError('\"delim\" and \"end_str\" arguments could not be in directory name!')
        self.mpath = self.directory + 'Matrix/'
        self.vpath = self.directory + 'Vector/'
        self.rpath = self.directory + 'Result/'
        self.row_num = row_num
        self.col_num = col_num
        self.size_of_signal = sys.getsizeof(end_str)
        self.matrix_create_mode = matrix_create_mode
        self.vector_create_mode = vector_create_mode
        self.encoding = encoding
        self.delim = delim
        self.end_str = end_str

    def create_directories(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.mpath):
            os.makedirs(self.mpath)
        if not os.path.exists(self.vpath):
            os.makedirs(self.vpath)
        if not os.path.exists(self.rpath):
            os.makedirs(self.rpath)

    def fill_matrix_unit(self):
        files = [f for f in os.listdir(self.mpath) if str(f).endswith('txt')]
        for f in files:
            os.remove(self.mpath + str(f))
        for i in range(int(self.row_num)):
            f = open(self.mpath + 'm%d.txt' % i, 'w')
            for j in range(int(self.col_num)):
                if i == j:
                    value = 1
                else:
                    value = 0
                f.write(str(value) + ' ')
            f.close()

    def fill_matrix_random(self):
        files = [f for f in os.listdir(self.mpath) if str(f).endswith('txt')]
        for f in files:
            os.remove(self.mpath + str(f))
        for i in range(int(self.row_num)):
            f = open(self.mpath + 'm%d.txt' % i, 'w')
            for j in range(int(self.col_num)):
                value = randint(0, 10)
                f.write(str(value) + ' ')
            f.close()

    def fill_vector_random(self):
        files = [f for f in os.listdir(self.vpath) if str(f).endswith('txt')]
        for f in files:
            os.remove(self.vpath + str(f))
        f = open(self.vpath + 'v.txt', 'w')
        for j in range(int(self.col_num)):
            value = randint(0, 10)
            f.write(str(value) + ' ')

    def create_data(self):
        self.create_directories()
        if self.matrix_create_mode == 'unit':
            self.fill_matrix_unit()
        elif self.matrix_create_mode == 'random':
            self.fill_matrix_random()
        if self.vector_create_mode == 'random':
            self.fill_vector_random()

    def change_data_volume(self, row_num=None, col_num=None):
        if row_num is not None:
            self.row_num = row_num
        if col_num is not None:
            self.col_num = col_num

    def change_data_creating_mode(self, matrix_create_mode=None, vector_create_mode=None):
        if matrix_create_mode is not None:
            self.matrix_create_mode = matrix_create_mode
        if vector_create_mode is not None:
            self.vector_create_mode = vector_create_mode

    def target(self):
        while True:
            try:
                self.sock.connect(self.address)
            except socket_error as err:
                if err.errno == 56:
                    break
            else:
                break
        arguments_to_send = self.directory + self.delim + str(self.row_num) + self.delim + str(self.col_num) + \
                            self.end_str
        self.sock.send(arguments_to_send.encode(self.encoding))
        self.sock.close()
