import logging

from dataclay_mds.etcd.etcd_handler import EtcdHandler
from dataclay_mds.logic.account_manager import AccountManager
from dataclay_mds.logic.session_manager import SessionManager


class MetadataService:

    def __init__(self):
        etcd_client = EtcdHandler()

        account_mgr = AccountManager(etcd_client)
        session_mgr = SessionManager(etcd_client)


    def new_account(self):
        pass