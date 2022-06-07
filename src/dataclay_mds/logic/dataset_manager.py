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

    @classmethod
    def from_json(cls, value):
        dataset = cls(value['name'], value['owner'],
            is_public=value['is_public'])
        return dataset

class DatasetManager:

    lock = 'lock_dataset'

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_dataset(self, dataset):
        # Store dataset in etcd
        self.etcd_client.put(dataset.key(), dataset.value())

    def get_dataset(self, name):
        # Get dataset from etcd and checks that it exists
        key = f'/dataset/{name}'
        value = self.etcd_client.get(key)[0]
        if value is None:
            raise Exception(f'Dataset {name} does not exists!')

        return Dataset.from_json(value)

    def new_dataset(self, dataset):
        # Creates a lock and checks that the dataset does not exists,
        # then creates a new dataset in etcd
        with self.etcd_client.lock(self.lock):
            if not self.etcd_client.get(dataset.key())[0]:
                self.etcd_client.put(dataset.key(), dataset.value())
            else:
                raise Exception(f'Dataset {dataset.name} already exists!')
