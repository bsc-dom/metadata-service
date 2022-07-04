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
    def from_json(cls, s):
        value = json.loads(s)
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


    def exists_dataset(self, name):
        """"Returns true if dataset exists"""

        key = f'/dataset/{name}'
        value = self.etcd_client.get(key)[0]
        return value is not None

    def new_dataset(self, dataset):
        """Creates a new dataset. Checks that the dataset doesn't exists."""

        with self.etcd_client.lock(self.lock):
            if self.exists_dataset(dataset.name):
                raise Exception(f'Dataset {dataset.name} already exists!')
            self.put_dataset(dataset)
