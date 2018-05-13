import socket
import tqdm
import time


class Host:

    def __init__(self, worker_num, args_lst, default_port, name, size_of_signal, encoding, worker_type, delim=',',
                 end_str=';', res_delim='|', result_type=int):
        self.try_params(args_lst, delim, end_str, res_delim)
        self.default_port = default_port
        self.name = name
        self.worker_num = worker_num
        self.args_lst = args_lst
        self.workers = []
        self.results = []
        self.sockets, self.connections = [], []
        self.size_of_signal = size_of_signal
        self.encoding = encoding
        self.worker_type = worker_type
        self.delim = delim
        self.end_str = end_str
        self.res_delim = res_delim
        self.result_type = result_type
        for _ in args_lst:
            self.results.append(None)
        for i in range(worker_num):
            self.sockets.append(socket.socket())
            self.connections.append(None)
            self.sockets[i].setblocking(0)
            self.sockets[i].bind(('', self.default_port + i))
            self.sockets[i].listen(1)
            self.workers.append(worker_type(address=(self.name, self.default_port + i),
                                            size_of_signal=self.size_of_signal, encoding=self.encoding,
                                            delim=self.delim, end_str=self.end_str, res_delim=self.res_delim,
                                            name='Worker #' + str(i), result_type=self.result_type))
        print('Workers were added.')

    def try_params(self, args_lst, delim=',', end_str=';', res_delim='|'):
        for args in args_lst:
            str_args = str(args)
            if delim in str_args or end_str in str_args or res_delim in str_args:
                raise '"delim", "end_str" and "res_delim" haven\'t to be in args_lst!'

    def start_all(self):
        for worker in self.workers:
            worker.start()

    def join_all(self):
        for worker in self.workers:
            worker.join()

    def data_exchange(self):
        while None in self.connections:
            for i in range(self.worker_num):
                try:
                    conn, addr = self.sockets[i].accept()
                except socket.error:
                    pass
                else:
                    self.connections[i] = conn
                    print('Host: connection between host and worker "%s" was accepted' % self.workers[i].name)
        worker_index = 0
        for args in self.args_lst:
            data = str(args) + self.delim
            self.connections[worker_index].send(data.encode(self.encoding))
            worker_index += 1
            if worker_index == self.worker_num:
                worker_index = 0
        self.args_lst.clear()
        for i in range(self.worker_num):
            self.connections[i].send(self.end_str.encode(self.encoding))
        buff = ''
        print('\nHost: a process of collecting data starts\n')
        tqdm.tqdm.monitor_interval = 0
        progress_bar = tqdm.tqdm(total=len(self.results), ncols=100, mininterval=0.0)
        while None in self.results:
            for i in range(self.worker_num):
                try:
                    data = self.connections[i].recv(self.size_of_signal)
                except socket.error:
                    pass
                else:
                    buff += data.decode(self.encoding)
            while len(buff) != 0:
                res = buff[:buff.find(self.res_delim)]
                buff = buff[buff.find(self.res_delim) + 1:]
                rindex, value = tuple(res.split(self.delim))
                rindex, value = int(rindex), self.result_type(value)
                self.results[rindex] = value
                progress_bar.update(1)
        time.sleep(1)
        print('\nHost: a process of collecting data was finished\n')
        for i in range(self.worker_num):
            self.sockets[i].close()
            print('Host: connection with worker "%s" was closed' % self.workers[i].name)

    def execute(self):
        self.start_all()
        self.data_exchange()
        self.join_all()
        return self.results
