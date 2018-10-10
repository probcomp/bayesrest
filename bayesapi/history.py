import pickle

def get_file_path(cfg, data_type):

    data_type_paths = { 'query':      cfg['file'],
                        'similarity': cfg['similarity_file'],
                        'anomaly':    cfg['anomaly_file']}

    if data_type in data_type_paths:
        return data_type_paths[data_type]

    return cfg['file']

def save(cfg, data, data_type="query"):
    path = get_file_path(cfg, data_type)
    with open(path, "wb") as fh:
        pickle.dump(data, fh)

def read(cfg, data_type="query"):
    path = get_file_path(cfg, data_type)
    with open(path, "rd") as fh:
        res = pickle.load(fh)
        return res
