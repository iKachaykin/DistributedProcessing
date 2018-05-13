import os, shutil
from Host import Host as Host
from StandardTaskClient import StandardTaskClient
from tqdm import tqdm


def clear_dir(dir):
    folder = dir
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    clear_dir('/users/ivankachaikin/PycharmProjects/ProjectFiles/ClientsData/')
    client_num = int(input('Host: input a number of clients: '))
    worker_num = int(input('Host: input a number of workers: '))
    default_port = int(input('Host: input the default port: '))
    row_num = int(input('Host: input a number of rows: '))
    col_num = int(input('Host: input a number of cols: '))
    clients = [StandardTaskClient('Client%d' % i, ('localhost', default_port + i),
                                  '/users/ivankachaikin/PycharmProjects/ProjectFiles/ClientsData/',
                                  row_num, col_num) for i in range(client_num)]
    localhost = Host(worker_num, client_num, default_port, 'localhost', 1024)
    print('Clients creating their data')
    tqdm.monitor_interval = 0
    for client in tqdm(clients, ncols=100):
        client.create_data()
    for i in range(client_num):
        clients[i].start()
    localhost.execute()
