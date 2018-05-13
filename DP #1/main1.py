import numpy as np
import time
from multiprocessing import pool
from multiprocessing import Process


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
    elem_num, worker_num = 10000, 2
    arguments = ((rindex, mpath, vpath) for rindex in range(elem_num))
    standard_pool = pool.Pool(worker_num)
    seconds = time.time()
    results = standard_pool.map(target, arguments)
    seconds = time.time() - seconds
    standard_pool.close()
    standard_pool.join()
    print(seconds)
    rfile = open(rpath + "r.txt", "w")
    for r in results:
        rfile.write("%d " % r)
    rfile.close()
