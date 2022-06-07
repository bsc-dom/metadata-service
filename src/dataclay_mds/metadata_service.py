import logging
import json

import etcd3

from dataclay_mds.logic.account_manager import AccountManager, Account
from dataclay_mds.logic.session_manager import SessionManager, Session
from dataclay_mds.logic.dataset_manager import DatasetManager, Dataset
from dataclay_mds.conf import settings

logger = logging.getLogger(__name__)


class MetadataService:

    def __init__(self):
        # Creates etcd client
        self.etcd_client = etcd3.client(settings.ETCD_HOST, settings.ETCD_PORT)

        # Creates managers for each class
        self.account_mgr = AccountManager(self.etcd_client)
        self.session_mgr = SessionManager(self.etcd_client)
        self.dataset_mgr = DatasetManager(self.etcd_client)

        logger.info("Initialized MetadataService")

    def new_account(self, username, password):
        # Creates a default dataset and puts it to etcd
        # TODO: Use a default name that cannot be taken by other users previously
        #       For example, {username}_ds
        # TODO: ¿Should I create a default dataset? If not, delete the creation
        # dataset = Dataset(username, username)
        account = Account(username, password)

        # Put to etcd
        # TODO: Create transaction for both updates
        self.account_mgr.new_account(account)
        # self.dataset_mgr.new_dataset(dataset)

        # TODO: Return a more interesting value
        logger.info(f'Created new account for {username}')
        return username

    def new_session(self, username, password, dataset_for_store):
        """"Registers a new session

        Validates the account credentials, and creates a new session
        associated to the account and the dataset_for_store.

        Args:
            username : Accounts username
            password : Accounts password
            dataset_for_store: Name of the dataset to store objects

        Raises:
            Exception('Account is not valid!'): If wrong credentials
        """
        # Validates account credentials
        account = self.account_mgr.get_account(username)
        if not account.validate(password):
            raise Exception('Account is not valid!')

        # Validates accounts access to dataset_for_store
        dataset = self.dataset_mgr.get_dataset(dataset_for_store)
        if (not dataset.is_public and dataset_for_store not in account.datasets):
            raise Exception(f'Account {username} cannot access {dataset_for_store} dataset!')

        # Creates a new session
        session = Session(username=username, datasets=account.datasets,
                          dataset_for_store=dataset_for_store)
        self.session_mgr.put_session(session)

        logger.info(f'Created new session for {username} with id {session.id}')
        return session.id

    def new_dataset(self, username, password, dataset_name):
        """"Registers a new dataset

        Validates the account credentials, and creates a new dataset
        associated to the account. It updates the account metadata
        to add access to the new dataset. The dataset name must bu
        unique.

        Args:
            username : Accounts username
            password : Accounts password
            dataset_name: Name of the new dataset. Must be unique.

        Raises:
            Exception('Account is not valid!'): If wrong credentials
        """
        # Validates account credentials
        account = self.account_mgr.get_account(username)
        if not account.validate(password):
            raise Exception('Account is not valid!')

        # Creates new dataset and updates account's list of datasets
        dataset = Dataset(dataset_name, username)
        account.datasets.append(dataset_name)

        # Put new dataset to etcd and updates account metadata
        # Order matters to check that dataset name is not registered
        self.dataset_mgr.new_dataset(dataset)
        self.account_mgr.put_account(account)

        logger.info(f'Created {dataset.name} dataset for {username} account')
