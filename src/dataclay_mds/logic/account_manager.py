import json

class AccountManager:
    
    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def new_account(self, username, password):
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

        # TODO: Validate admin account
        # TODO: Check that the username does not exists

        # Create json account
        account = dict()
        account['username'] = username
        account['password'] = password
        account['role'] = 'NORMAL'
        account['namespaces'] = [None]
        account['datatasets'] = [None]

        # Store account in etcd
        key = f'/account/{username}'
        value = json.dumps(account)
        self.etcd_client.put(key, value)

        return username
        

