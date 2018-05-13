import numpy as np
import time
from Host import Host
from StandardTaskWorker import StandardTaskWorker


def target(args):
    rindex, mpath, vpath = args
    mfile = open(mpath + "m%d.txt" % rindex, "r")
    buf = mfile.read().split(" ")
    mfile.close()
    buf = buf[:len(buf) - 1]
    row = np.array(buf, dtype=int)
    vfile = open(vpath + "v0.txt", "r")
    buf = vfile.read().split(" ")
    vfile.close()
    buf = buf[:len(buf) - 1]
    vector = np.array(buf, dtype=int)
    return np.dot(row, vector)


if __name__ == "__main__":
    mpath, vpath, rpath = "/users/ivankachaikin/PycharmProjects/ProjectFiles/Matrix/", \
                          "/users/ivankachaikin/PycharmProjects/ProjectFiles/Vector/", \
                          "/users/ivankachaikin/PycharmProjects/ProjectFiles/Results/"
    worker_num = int(input('Host: input a number of workers: '))
    default_port = int(input('Host: input the default port: '))
    elem_num = 100000
    args_lst = [str(i) for i in range(elem_num)]
    localhost = Host(worker_num, args_lst, default_port, 'localhost', 1024, 'utf-8', StandardTaskWorker)
    seconds = time.time()
    results_1 = localhost.execute()
    seconds = time.time() - seconds - 1
    print('Localhost time is: %f' % seconds)
    # arg_lst = ((rindex, mpath, vpath) for rindex in range(elem_num))
    # standard_pool = pool.Pool(worker_num)
    # seconds = time.time()
    # results_2 = standard_pool.map(target, arg_lst)
    # seconds = time.time() - seconds
    # print('Pool time is: %f' % seconds)
    # standard_pool.close()
    # standard_pool.join()
    # for res1, res2 in zip(results_1, results_2):
    #     if res1 != res2:
    #         print('Error! res1 = %d != res2 = %d' % (res1, res2))
    #         sys.exit()
    # print('No errors!')
    rfile = open(rpath + "r.txt", "w")
    for r in results_1:
        rfile.write("%d " % r)
    rfile.close()
