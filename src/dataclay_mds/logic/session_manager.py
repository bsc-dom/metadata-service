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

        

class SessionManager:

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_session(self, session):

        # Store session in etcd
        key = f'/session/{session.id}'
        value = json.dumps(session.__dict__)
        self.etcd_client.put(key, value)
