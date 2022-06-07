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
        """"Registers a new account

        Creates a new account. Checks that the username is not registered.

        Args:
            username : Accounts username
            password : Accounts password
        """

        # TODO: Ask for admin credentials for creating the account.

        # Creates new account and put it to etcd
        account = Account(username, password)
        self.account_mgr.new_account(account)

        logger.info(f'Created new account for {username}')

    def new_session(self, username, password, default_dataset):
        """"Registers a new session

        Validates the account credentials, and creates a new session
        associated to the account and the default_dataset.

        Args:
            username : Accounts username
            password : Accounts password
            default_dataset: Name of the dataset to store objects

        Raises:
            Exception('Account is not valid!'): If wrong credentials
        """

        # Validates account credentials
        account = self.account_mgr.get_account(username)
        if not account.validate(password):
            raise Exception('Account is not valid!')

        # Validates accounts access to default_dataset
        dataset = self.dataset_mgr.get_dataset(default_dataset)
        if (not dataset.is_public and default_dataset not in account.datasets):
            raise Exception(f'Account {username} cannot access {default_dataset} dataset!')

        # Creates a new session
        session = Session(username=username, datasets=account.datasets,
                          default_dataset=default_dataset)
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
