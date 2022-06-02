import logging

import etcd3

from dataclay_mds.logic.account_manager import AccountManager, Account
from dataclay_mds.logic.session_manager import SessionManager, Session
from dataclay_mds.logic.dataset_manager import DatasetManager, Dataset
from dataclay_mds.conf import settings

logger = logging.getLogger(__name__)

class MetadataService:

    def __init__(self):
        # Creates etcd client
        etcd_client = etcd3.client(settings.ETCD_HOST, settings.ETCD_PORT)

        # Creates managers for each class
        self.account_mgr = AccountManager(etcd_client)
        self.session_mgr = SessionManager(etcd_client)
        self.dataset_mgr = DatasetManager(etcd_client)

        logger.info("Initialized MetadataService")


    def new_account(self, username, password):
        # Creates a default dataset and puts it to etcd
        # TODO: Use a default name that cannot be taken by other users previously
        #       For example, {username}_ds
        dataset = Dataset(username)
        account = Account(username, password, datasets=[dataset.name])

        # Put to etcd
        self.account_mgr.new_account(account)
        self.dataset_mgr.put_dataset(dataset)

        # TODO: Return a more interesting value
        logger.info(f'Created new account for {username}')
        return username

    def new_session(self, username, password, datasets, dataset_for_store):
        # TODO: Add namespaces (if needed)
        # Validate account
        account = self.account_mgr.get_account(username)
        if not account.validate(password):
            raise Exception('Account is not valid!')

        # Creates a new session and puts it to etcd
        session = Session(
            username=username,
            datasets=datasets, 
            dataset_for_store=dataset_for_store
        )
        self.session_mgr.put_session(session)

        logger.info(f'Created new session for {username}, with id {session.id}')
        return session.id

    def new_dataset(self, username, password, dataset_name):
        # Validate account
        account = self.account_mgr.get_account(username)
        if not account.validate(password):
            raise Exception('Account is not valid!')

        dataset = Dataset(dataset_name)
        self.dataset_mgr.put_dataset(dataset)


