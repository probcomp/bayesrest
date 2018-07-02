import pickle

def save(path, data):
    with open(path, "wb") as fh:
        pickle.dump(data, fh)

def read(path):
    with open(path, "rd") as fh:
        res = pickle.load(fh)
        return res
