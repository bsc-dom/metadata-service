import json
import logging

logger = logging.getLogger(__name__)

class Account:
    def __init__(self, username, password=None, 
        role='NORMAL', namespaces=[None], datasets=[None]):
        self.username = username
        self.password = password
        self.role = role
        self.namespaces = namespaces
        self.datasets = datasets

    @classmethod
    def from_json(cls, value):
        account = cls(value['username'],
            password=value['password'],
            role=value['role'],
            namespaces=value['namespaces'],
            datasets=value['datasets'])
        return account


class AccountManager:
    
    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_account(self, account):
        """"Registers a new account
        
        If the username is already registered, the account is not created

        Args:
            username : The username of the new account
            password : The password of the new account

        Returns:
            The username of the new account

        Raises:
            NotImplementedError: If no sound is set for the animal or passed in as a 
                parameter.
        """

        # TODO: Validate admin account (maybe not here)
        # TODO: Check that the username does not exists

        # Store account in etcd
        key = f'/account/{account.username}'
        value = json.dumps(account.__dict__)
        self.etcd_client.put(key, value)

        return account.username

    def get_account(self, username):
        key = f'/account/{username}'
        value = json.loads(self.etcd_client.get(key)[0])
        account = Account(username, 
            password=value['password'],
            role=value['role'],
            namespaces=value['namespaces'],
            datasets=value['datasets'])
        return account
        
    def exists(self, username):
        """"Checks if account exists
        
        Returns:
            A tuple with a boolean, and the account if it exists
        """
        key = f'/account/{username}'
        value = self.etcd_client.get(key)[0]
        return (value is not None, value)

    def new_account(self, account):
        key = f'/account/{account.username}'
        value = json.dumps(account.__dict__)

        # Creates a lock and checks that the username does not exists
        with self.etcd_client.lock('lock_account'):
            if not self.etcd_client.get(key)[0]:
                self.etcd_client.put(key, value)
            else:
                raise Exception('Account already exists!')

    def validate_account(self, username, password, role='NORMAL'):
        # Checks if account exists
        exists, value = self.exists(username)
        if not exists:
            raise Exception('Account does not exists!')
    
        value = json.loads(value)
        is_valid = True

        # Checks account role
        if value['role'] != role:
            is_valid = False
            logger.debug(f'Role {role} does not match account role {value["role"]}.')
        
        # Checks password
        if value['password'] != password:
            is_valid = False
            logger.debug(f'Password does not match!')

        return is_valid



        