import json
import uuid


class Session:
    def __init__(self, username, namespaces=[],
        datasets=[], default_dataset=None):
        self.id = str(uuid.uuid4())
        self.username = username
        self.namespaces = namespaces
        self.datasets = datasets
        self.default_dataset = default_dataset

    def key(self):
        return f'/session/{self.id}'

    def value(self):
        return json.dumps(self.__dict__)
        

class SessionManager:

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_session(self, session):
        self.etcd_client.put(session.key(), session.value())

    def delete_session(self, id):
        key = f'/session/{id}'
        self.etcd_client.delete(key)
