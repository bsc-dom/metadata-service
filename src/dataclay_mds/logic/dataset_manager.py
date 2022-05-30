import json
import uuid


class Dataset:
    def __init__(self, name, is_public=False):
        self.name = name
        self.is_public = is_public       

class DatasetManager:

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_dataset(self, dataset):
        
        # TODO: Check dataset does not exists already

        # Store dataset in etcd
        key = f'/dataset/{dataset.name}'
        value = json.dumps(dataset.__dict__)
        self.etcd_client.put(key, value)
