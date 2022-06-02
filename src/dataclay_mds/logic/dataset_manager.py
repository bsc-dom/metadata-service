import json
import uuid


class Dataset:
    def __init__(self, name, owner, is_public=False):
        self.name = name
        self.owner = owner
        self.is_public = is_public

    def key(self):
        return f'/dataset/{self.name}'

    def value(self):
        return json.dumps(self.__dict__)

class DatasetManager:

    lock = 'lock_dataset'

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_dataset(self, dataset):
        
        # TODO: Check dataset does not exists already

        # Store dataset in etcd
        key = f'/dataset/{dataset.name}'
        value = json.dumps(dataset.__dict__)
        self.etcd_client.put(key, value)

    def new_dataset(self, dataset):
        key = f'/dataset/{dataset.name}'
        value = json.dumps(dataset.__dict__)

        # Creates a lock and checks that the dataset does not exists
        with self.etcd_client.lock(self.lock):
            if not self.etcd_client.get(key)[0]:
                self.etcd_client.put(key, value)
            else:
                raise Exception(f'Dataset {dataset.name} already exists!')
