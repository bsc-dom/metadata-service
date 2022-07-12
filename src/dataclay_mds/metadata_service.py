import logging
import json
import uuid

import etcd3
from dataclay_common.managers.account_manager import AccountManager, Account
from dataclay_common.managers.session_manager import SessionManager, Session
from dataclay_common.managers.dataset_manager import DatasetManager, Dataset
from dataclay_common.managers.object_manager import (
    ObjectManager,
    ObjectRegisterInfo,
    ObjectMetadata,
)
from dataclay_common.managers.dataclay_manager import (
    DataclayManager,
    ExecutionEnvironment,
)

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
        if not account.validate(password):
            raise Exception("Account is not valid!")

        # Validates accounts access to default_dataset
        dataset = self.dataset_mgr.get_dataset(default_dataset)
        if not dataset.is_public and default_dataset not in account.datasets:
            raise Exception(
                f"Account {username} cannot access {default_dataset} dataset!"
            )

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
        if not account.validate(password):
            raise Exception("Account is not valid!")

        # Creates new dataset and updates account's list of datasets
        dataset = Dataset(dataset_name, username)
        account.datasets.append(dataset_name)

        # Put new dataset to etcd and updates account metadata
        # Order matters to check that dataset name is not registered
        self.dataset_mgr.new_dataset(dataset)
        self.account_mgr.put_account(account)

        logger.info(f"Created {dataset.name} dataset for {username} account")

    def close_session(self, id):
        """Close session by id

        Args:
            id : Session id
        """

        # TODO: Check that session exists
        # TODO: Don't delete session, but set a variable as closed
        self.session_mgr.delete_session(id)

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

    def register_objects(self, objects_info, backend_id, lang):
        objects_id = []
        for object_info in objects_info:
            object_id = self.register_object(object_info, backend_id, lang)
            objects_id.append(object_id)

        return objects_id

    def register_object(self, object_info, backend_id, lang):
        # TODO: Get default dataset from account

        object_metadata = ObjectMetadata(
            object_info.object_id,
            object_info.class_id,
            object_info.dataset_name,
            backend_id,
            "LANG_PYTHON",
            "TEST",
            is_read_only=False,
            alias=object_info.alias,
        )
        self.object_mgr.register_object(object_metadata)
        pass
