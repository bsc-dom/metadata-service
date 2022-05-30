# TODO: Remove class

import etcd3
from dataclay_mds.conf import settings

class EtcdHandler:

    def __init__(self):
        self.etcd = etcd3.client(settings.ETCD_HOST, settings.ETCD_PORT)

    # def initialize(self):
    #     self.etcd = etcd3.client(settings.ETCD_HOST, settings.ETCD_PORT)

    def get(self, key):
        return self.etcd.get(key)

    def put(self, key, value):
        self.etcd.put(key, value)