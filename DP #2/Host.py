import socket
import tqdm
import time
from StandardTaskWorker import StandardTaskWorker
from queue import Queue


class Host:

    def __init__(self, worker_num, client_num, default_port, name, size_of_signal, encoding='utf-8',
                 worker_type=StandardTaskWorker, delim=',', end_str=';', res_delim='|', result_type=int):
        self.default_port = default_port
        self.name = name
        self.client_num = client_num
        self.worker_num = worker_num
        self.clients_queries = []
        self.workers, self.args_lst, self.results = [], [], []
        self.sockets_for_workers, self.connections_with_workers = [], []
        self.sockets_for_clients, self.connections_with_clients = [], []
        self.size_of_signal = size_of_signal
        self.encoding = encoding
        self.worker_type = worker_type
        self.delim = delim
        self.end_str = end_str
        self.res_delim = res_delim
        self.result_type = result_type
        for i in range(client_num):
            self.sockets_for_clients.append(socket.socket())
            self.connections_with_clients.append(None)
            self.sockets_for_clients[i].setblocking(0)
            self.sockets_for_clients[i].bind(('', self.default_port))
            self.sockets_for_clients[i].listen(1)
            self.default_port += 1
        for i in range(worker_num):
            self.sockets_for_workers.append(socket.socket())
            self.connections_with_workers.append(None)
            self.sockets_for_workers[i].setblocking(0)
            self.sockets_for_workers[i].bind(('', self.default_port))
            self.sockets_for_workers[i].listen(1)
            self.workers.append(self.worker_type(address=(self.name, self.default_port),
                                            size_of_signal=self.size_of_signal, encoding=self.encoding,
                                            delim=self.delim, end_str=self.end_str, res_delim=self.res_delim,
                                            name='Worker #' + str(i), result_type=self.result_type))
            self.default_port += 1
        print('Workers were added.')

    def try_params(self, args_lst, delim=',', end_str=';', res_delim='|'):
        for args in args_lst:
            str_args = str(args)
            if delim in str_args or end_str in str_args or res_delim in str_args:
                raise ValueError('"delim", "end_str" and "res_delim" haven\'t to be in args_lst!')

    def start_all(self):
        for worker in self.workers:
            worker.start()

    def join_all(self):
        for worker in self.workers:
            worker.join()

    def terminate_all(self):
        for worker in self.workers:
            worker.terminate()

    def data_exchange(self):
        while None in self.connections_with_workers:
            for i in range(self.worker_num):
                try:
                    conn, addr = self.sockets_for_workers[i].accept()
                except socket.error:
                    pass
                else:
                    self.connections_with_workers[i] = conn
                    print('Host: connection between host and worker "%s" was accepted' % self.workers[i].name)
        worker_index = 0
        for args in self.args_lst:
            data = str(args) + self.delim
            self.connections_with_workers[worker_index].send(data.encode(self.encoding))
            worker_index += 1
            if worker_index == self.worker_num:
                worker_index = 0
        self.args_lst.clear()
        for i in range(self.worker_num):
            self.connections_with_workers[i].send(self.end_str.encode(self.encoding))
        buff = ''
        print('\nHost: a process of collecting data starts\n')
        tqdm.tqdm.monitor_interval = 0
        progress_bar = tqdm.tqdm(total=len(self.results), ncols=100, mininterval=0.0)
        while None in self.results:
            for i in range(self.worker_num):
                try:
                    data = self.connections_with_workers[i].recv(self.size_of_signal)
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
        for i in range(self.worker_num):
            self.connections_with_workers[i].close()
        print('\nHost: a process of collecting data was finished\n')
        for i in range(self.worker_num):
            self.sockets_for_workers[i].close()
            print('Host: connection with worker "%s" was closed' % self.workers[i].name)

    def write_results(self, rpath):
        rfile = open(rpath + "r.txt", "w")
        for r in self.results:
            rfile.write("%d " % r)
        rfile.close()

    def reset_results(self, results_num):
        self.results.clear()
        self.results = [None for i in range(results_num)]

    def create_args(self, args_num):
        self.args_lst.clear()
        self.args_lst = [str(i) for i in range(args_num)]

    def refresh_all_paths(self, new_dir):
        for i in range(self.worker_num):
            self.workers[i].set_mpath(new_dir + 'Matrix/')
            self.workers[i].set_vpath(new_dir + 'Vector/')

    def refresh_workers(self):
        self.workers.clear()
        self.connections_with_workers.clear()
        self.sockets_for_workers.clear()
        for i in range(self.worker_num):
            self.sockets_for_workers.append(socket.socket())
            self.connections_with_workers.append(None)
            self.sockets_for_workers[i].setblocking(0)
            self.sockets_for_workers[i].bind(('', self.default_port))
            self.sockets_for_workers[i].listen(1)
            self.workers.append(self.worker_type(address=(self.name, self.default_port),
                                            size_of_signal=self.size_of_signal, encoding=self.encoding,
                                            delim=self.delim, end_str=self.end_str, res_delim=self.res_delim,
                                            name='Worker #' + str(i), result_type=self.result_type))
            self.default_port += 1
        print('Host: workers were refreshed')

    def get_clients_queries(self):
        while None in self.connections_with_clients:
            for i in range(self.client_num):
                try:
                    conn, addr = self.sockets_for_clients[i].accept()
                except socket.error:
                    pass
                else:
                    self.connections_with_clients[i] = conn
        for i in range(self.client_num):
            buffer = ''
            while not (self.end_str in buffer):
                try:
                    encoded_data = self.connections_with_clients[i].recv(self.size_of_signal)
                except socket.error:
                    pass
                else:
                    buffer += encoded_data.decode(self.encoding)
            self.clients_queries.insert(0, buffer)
        self.close_all_connections_with_clients()

    def close_all_connections_with_clients(self):
        for i in range(self.client_num):
            self.sockets_for_clients[i].close()

    def execute(self):
        self.get_clients_queries()
        while len(self.clients_queries) > 0:
            directory, row_num, col_num = tuple(self.clients_queries.pop().replace(self.end_str, '').split(self.delim))
            row_num, col_num = int(row_num), int(col_num)
            print('Host: processing the query from client \"%s\"' %
                  directory[directory.rfind('/', 0, directory.rfind('/')) + 1:directory.rfind('/')])
            self.refresh_all_paths(directory)
            self.reset_results(row_num)
            self.create_args(row_num)
            self.start_all()
            self.data_exchange()
            self.join_all()
            self.terminate_all()
            self.write_results(directory + 'Result/')
            self.refresh_workers()
        self.workers.clear()
