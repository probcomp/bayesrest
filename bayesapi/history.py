import pickle

def save(cfg, data):
    path = cfg['file']
    with open(path, "wb") as fh:
        pickle.dump(data, fh)

def read(cfg):
    path = cfg['file']
    with open(path, "rd") as fh:
        res = pickle.load(fh)
        return res
