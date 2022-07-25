import logging
import json
import uuid

import etcd3
from dataclay_common.managers.account_manager import AccountManager, Account
from dataclay_common.managers.session_manager import SessionManager, Session
from dataclay_common.managers.dataset_manager import DatasetManager, Dataset
from dataclay_common.managers.object_manager import ObjectManager, ObjectMetadata, Alias
from dataclay_common.managers.dataclay_manager import DataclayManager, ExecutionEnvironment
from dataclay_common.exceptions.exceptions import *

FEDERATOR_ACCOUNT_USERNAME = "Federator"
EXTERNAL_OBJECTS_DATASET_NAME = "ExternalObjects"

logger = logging.getLogger(__name__)


class MetadataService:
    def __init__(self, etcd_host, etcd_port):
        # Creates etcd client
        self.etcd_client = etcd3.client(etcd_host, etcd_port)

        # Creates managers for each class
        self.account_mgr = AccountManager(self.etcd_client)
        self.session_mgr = SessionManager(self.etcd_client)
        self.dataset_mgr = DatasetManager(self.etcd_client)
        self.object_mgr = ObjectManager(self.etcd_client)
        self.dataclay_mgr = DataclayManager(self.etcd_client)

        # Set Dataclay id
        self.dataclay_id = str(uuid.uuid4())

        logger.info("Initialized MetadataService")

    def new_account(self, username, password):
        """ "Registers a new account

        Creates a new account. Checks that the username is not registered.

        Args:
            username : Accounts username
            password : Accounts password
        """

        # TODO: Ask for admin credentials for creating the account.

        # Creates new account and put it to etcd
        account = Account(username, password)
        self.account_mgr.new_account(account)

        logger.info(f"Created new account for {username}")

    def new_session(self, username, password, default_dataset):
        """ "Registers a new session

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
        if not account.verify(password):
            raise AccountInvalidCredentialsError(username)

        # Validates accounts access to default_dataset
        dataset = self.dataset_mgr.get_dataset(default_dataset)
        if not dataset.is_public and default_dataset not in account.datasets:
            raise DatasetIsNotAccessibleError(default_dataset, username)

        # Creates a new session
        # TODO: ¿Remove namespaces from Session and Account?
        session = Session(
            username=username,
            datasets=account.datasets,
            namespaces=account.namespaces,
            default_dataset=default_dataset,
        )
        self.session_mgr.put_session(session)

        logger.info(f"Created new session for {username} with id {session.id}")
        return session.id

    def new_dataset(self, username, password, dataset_name):
        """ "Registers a new dataset

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
        if not account.verify(password):
            raise AccountInvalidCredentialsError(username)

        # Creates new dataset and updates account's list of datasets
        dataset = Dataset(dataset_name, username)
        account.datasets.append(dataset_name)

        # Put new dataset to etcd and updates account metadata
        # Order matters to check that dataset name is not registered
        self.dataset_mgr.new_dataset(dataset)
        self.account_mgr.put_account(account)

        logger.info(f"Created {dataset.name} dataset for {username} account")

    def close_session(self, session_id):
        """Close session by id"""

        session = self.session_mgr.get_session(session_id)
        if not session.is_active:
            raise SessionIsNotActiveError(session_id)

        session.is_active = False
        self.session_mgr.put_session(session)

    def get_dataclay_id(self):
        """Get the dataclay id"""

        return self.dataclay_id

    def get_all_execution_environments(self, language, get_external, from_backend):
        """Get all execution environments"""

        # TODO: get_external should
        # TODO: Use exposed_ip_for_client if not from_backend to hide information?
        return self.dataclay_mgr.get_all_execution_environments(language)

    def autoregister_ee(self, id, name, hostname, port, lang):
        """Autoregister execution environment"""

        # TODO: Check if ee already exists. If so, update its information.
        # TODO: Check connection to ExecutionEnvironment
        exe_env = ExecutionEnvironment(id, name, hostname, port, lang, self.dataclay_id)
        self.dataclay_mgr.new_execution_environment(exe_env)
        # TODO: Deploy classes to backend? (better call from ee)

    ###################
    # Object Metadata #
    ###################

    def register_object(self, session_id, object_md):

        # TODO: If session_id is none, set the object_md owner
        #       and the dataset (is also none) to federation default

        # Checks that session exists and is active
        session = self.session_mgr.get_session(session_id)
        if not session.is_active:
            raise SessionIsNotActiveError(session_id)

        object_md.owner = session.username

        # Checks that the account has access to the dataset
        if object_md.dataset_name != session.default_dataset:
            dataset = self.dataset_mgr.get_dataset(object_md.dataset_name)
            if not dataset.is_public:
                account = self.account_mgr.get_account(session.username)
                if object_md.dataset_name not in account.datasets:
                    raise DatasetIsNotAccessibleError(object_md.dataset_name, account.username)

        self.object_mgr.register_object(object_md)

    def get_object_from_alias(self, session_id, alias_name, dataset_name):

        # Checks that session exists and is active
        session = self.session_mgr.get_session(session_id)
        if not session.is_active:
            raise SessionIsNotActiveError(session_id)

        # Check datset_name empty or None
        if not dataset_name:
            dataset_name = session.default_dataset
        elif dataset_name != session.default_dataset:
            # Checks that the account has access to the dataset
            dataset = self.dataset_mgr.get_dataset(dataset_name)
            if not dataset.is_public:
                account = self.account_mgr.get_account(session.username)
                if dataset_name not in account.datasets:
                    raise DatasetIsNotAccessibleError(dataset_name, account.username)

        alias = self.object_mgr.get_alias(alias_name, dataset_name)
        object_md = self.object_mgr.get_object_md(alias.object_id)
        return alias.object_id, object_md.class_id, object_md.execution_environment_ids[0]

    def delete_alias(self, session_id, alias_name, dataset_name):

        # Checks that session exist and is active
        session = self.session_mgr.get_session(session_id)
        if not session.is_active:
            raise SessionIsNotActiveError(session_id)

        # If dataset is None or empty, set to session's default_dataset
        if not dataset_name:
            dataset_name = session.default_dataset

        self.object_mgr.delete_alias(alias_name, dataset_name)
