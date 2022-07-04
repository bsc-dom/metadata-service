import json
import uuid


class ExecutionEnvironment:
    def __init__(self, id, hostname, name, port, language):
        # TODO: Create new uuid if id is none
        self.id = id
        self.hostname = hostname
        self.name = name
        self.port = port
        self.language = language

    def key(self):
        return f'/executionenvironment/{self.id}'

    def value(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, s):
        value = json.loads(s)
        execution_environment = cls()
        return execution_environment


class DataclayManager:

    lock = 'lock_dataclay'

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_ee(self, exe_env):
        """Put execution environment to etcd"""

        self.etcd_client.put(exe_env.key(), exe_env.value())

    def get_all_execution_environments(self):
        """Get all execution environments"""

        prefix = '/executionenvironment/'
        values = self.etcd_client.get_prefix(prefix)
        execution_environments = dict()
        for value, metadata in values:
            key = metadata.key.split('/')[-1]
            execution_environments[key] = ExecutionEnvironment.from_json(value)
        return execution_environments

    def exists_ee(self, id):
        """"Returns true if the execution environment exists"""

        key = f'/executionenvironment/{id}'
        value = self.etcd_client.get(key)[0]
        return value is not None

    def new_execution_environment(self, exe_env):
        """Creates a new execution environment. Checks that the it doesn't exists"""

        with self.etcd_client.lock(self.lock):
            if self.exists_ee(exe_env.id):
                raise Exception(f'ExecutionEnvironment {exe_env.id} already exists!')
            self.put_ee(exe_env)
