

class SessionManager:

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client
