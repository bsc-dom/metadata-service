import logging
import json
import uuid

import etcd3

from dataclay_common.managers.account_manager import AccountManager, Account
from dataclay_common.managers.session_manager import SessionManager, Session
from dataclay_common.managers.dataset_manager import DatasetManager, Dataset
from dataclay_common.managers.object_manager import ObjectManager, ObjectMetadata, Alias
from dataclay_common.managers.metaclass_manager import MetaclassManager, Metaclass
from dataclay_common.managers.dataclay_manager import (
    DataclayManager,
    ExecutionEnvironment,
    Dataclay,
)
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
        self.metaclass_mgr = MetaclassManager(self.etcd_client)
        self.dataclay_mgr = DataclayManager(self.etcd_client)

        logger.info("Initialized MetadataService")

    def autoregister_mds(self, id, hostname, port, is_this=False):
        """Autoregister Metadata Service"""
        dataclay = Dataclay(id, hostname, port, is_this)
        self.dataclay_mgr.new_dataclay(dataclay)

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

    def new_session(self, username, password, dataset_name):
        """ "Registers a new session

        Validates the account credentials, and creates a new session
        associated to the account and the dataset_name.

        Args:
            username : Accounts username
            password : Accounts password
            dataset_name: Name of the dataset to store objects

        Raises:
            Exception('Account is not valid!'): If wrong credentials
        """

        # Validates account credentials
        account = self.account_mgr.get_account(username)
        if not account.verify(password):
            raise AccountInvalidCredentialsError(username)

        # Validates accounts access to dataset_name
        dataset = self.dataset_mgr.get_dataset(dataset_name)
        if not dataset.is_public and dataset_name not in account.datasets:
            raise DatasetIsNotAccessibleError(dataset_name, username)

        # Creates a new session
        # TODO: ¿Remove namespaces from Session and Account?
        session = Session(
            id=uuid.uuid4(),
            username=username,
            dataset_name=dataset_name,
            is_active=True,
        )
        self.session_mgr.put_session(session)

        logger.info(f"Created new session for {username} with id {session.id}")
        return session

    def get_session(self, session_id):
        return self.session_mgr.get_session(session_id)

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

        # TODO: decide if close session remove the entry from etcd
        #       or just set the flag is_active to false

        # session = self.session_mgr.get_session(session_id)
        # if not session.is_active:
        #     raise SessionIsNotActiveError(session_id)

        # session.is_active = False
        # self.session_mgr.put_session(session)

        if not self.session_mgr.exists_session(session_id):
            raise SessionDoesNotExistError(session_id)
        # self.session_mgr.delete_session(session_id)

    def get_dataclay_id(self):
        """Get the dataclay id"""
        dataclay = self.dataclay_mgr.get_dataclay("this")
        return dataclay.id

    def get_storage_location(self, sl_name):
        return self.dataclay_mgr.get_storage_location(sl_name)

    def get_all_execution_environments(self, language, get_external=True, from_backend=False):
        """Get all execution environments"""

        # TODO: get_external should
        # TODO: Use exposed_ip_for_client if not from_backend to hide information?
        return self.dataclay_mgr.get_all_execution_environments(language)

    def autoregister_ee(self, id, hostname, port, sl_name, lang):
        """Autoregister execution environment"""

        # TODO: Check if ee already exists. If so, update its information.
        # TODO: Check connection to ExecutionEnvironment
        exe_env = ExecutionEnvironment(id, hostname, port, sl_name, lang, self.get_dataclay_id())
        self.dataclay_mgr.new_execution_environment(exe_env)
        # TODO: Deploy classes to backend? (better call from ee)

    ###################
    # Object Metadata #
    ###################

    def register_object(self, session_id, object_md):

        # NOTE: If only EE can register objects, no need to check session
        # Checks that session exists and is active
        # session = self.session_mgr.get_session(session_id)
        # if not session.is_active:
        #     raise SessionIsNotActiveError(session_id)

        # NOTE: If a session can just access one dataset, then this
        # dataset will always be the session's default dataset.
        # object_md.dataset_name = session.dataset_name

        self.object_mgr.register_object(object_md)

    def update_object(self, session_id, object_md):

        # NOTE: If only EE can update objects, no need to check session
        # Checks that session exists and is active
        # session = self.session_mgr.get_session(session_id)
        # if not session.is_active:
        #     raise SessionIsNotActiveError(session_id)

        # NOTE: If a session can just access one dataset, then this
        # dataset will always be the session's default dataset.
        # object_md.dataset_name = session.dataset_name

        self.object_mgr.update_object(object_md)

    def get_object_from_alias(self, session_id, alias_name, dataset_name, check_session=True):
        # TODO: Create generic get_object_md, that can be obtained with alias + datset
        #       or with object_id. It should return an ObjectMetadata object.

        if check_session:
            # Checks that session exists and is active
            session = self.session_mgr.get_session(session_id)
            if not session.is_active:
                raise SessionIsNotActiveError(session_id)

            # Checks that datset_name is empty or equal to session's dataset
            if not dataset_name:
                dataset_name = session.dataset_name
            elif dataset_name != session.dataset_name:
                raise DatasetIsNotAccessibleError(dataset_name, session.username)

        alias = self.object_mgr.get_alias(alias_name, dataset_name)
        object_md = self.object_mgr.get_object_md(alias.object_id)
        return alias.object_id, object_md.class_id, object_md.execution_environment_ids[0]

    def delete_alias(self, session_id, alias_name, dataset_name, check_session=True):

        # NOTE: If the session is not checked, we supose the dataset_name is correct
        #       since only the EE is able to set check_session to False
        if check_session:
            # Checks that session exist and is active
            session = self.session_mgr.get_session(session_id)
            if not session.is_active:
                raise SessionIsNotActiveError(session_id)

            # Check that the dataset_name is the same as session's dataset
            if not dataset_name:
                dataset_name = session.dataset_name
            elif dataset_name != session.dataset_name:
                raise DatasetIsNotAccessibleError(dataset_name, session.username)

        self.object_mgr.delete_alias(alias_name, dataset_name)

    def get_metaclass(self, metaclass_id):
        return self.metaclass_mgr.get_metaclass(metaclass_id)
