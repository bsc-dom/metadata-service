import etcd3

class EtcdHandler:

    def __init__(self):
        pass

    def initialize(self):
        self.etcd = etcd3.client(settings.logicmodule_host, 2379)
