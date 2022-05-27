import logging

from dataclay_mds.etcd.etcd_handler import EtcdHandler
from dataclay_mds.logic.account_manager import AccountManager
from dataclay_mds.logic.session_manager import SessionManager

logger = logging.getLogger(__name__)

class MetadataService:

    def __init__(self):
        etcd_client = EtcdHandler()

        self.account_mgr = AccountManager(etcd_client)
        self.session_mgr = SessionManager(etcd_client)

        logger.info("Initialized MetadataService")


    def new_account(self, username, password):
        self.account_mgr.new_account(username, password)