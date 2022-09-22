import itertools
import pickle
import os

max_file_size = 10_000

def load(path):
    ls = os.listdir(path)
    qt = {}
    for n,file in enumerate(ls):
        if ".pickle" in file:
            with open(path+file, 'rb') as f:
                qt.update(pickle.load(f))
        pprint(n+1, len(ls), path.split("\\")[-1])
    return qt

def pprint(start, end, name):
    os.system("cls")
    print(name)
    print(str(round(100/end*start))+f" %\n{start} / {end}")

def save(path, qt):
    ls = os.listdir(path)
    for file in ls:
        if ".pickle" in file:
            os.remove(path+file)
    div = divmod(len(qt), max_file_size)
    i = 0
    for i in range(div[0]):
        with open(path+f"\\qt_{str(i)}.pickle", "wb") as f:
            pickle.dump(dict(itertools.islice(qt.items(), max_file_size*i, max_file_size+max_file_size*i)),f, pickle.HIGHEST_PROTOCOL)
        pprint(i+1, div[0]+1, path.split("\\")[-1])
    if div[1] > 0:
        with open(path+f"\\qt_{str(i+1)}.pickle", "wb") as f:
            pickle.dump(dict(itertools.islice(qt.items(), len(qt)-div[1], len(qt))),f, pickle.HIGHEST_PROTOCOL)
        pprint(i+(1 if div[0]==0 else 2), div[0]+1, path.split("\\")[-1])