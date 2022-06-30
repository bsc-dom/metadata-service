import json
import uuid


class ExecutionEnvironment:
    def __init__(self, id, hostname, name, port, language):
        self.id = id
        self.hostname = hostname
        self.name = name
        self.port = port
        self.language = language

    def key(self):
        return f'/executionenvironment/{self.name}'

    def value(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, s):
        value = json.loads(s)
        execution_environment = cls()
        return execution_environment


class ExecutionEnvironmentManager:

    lock = 'lock_executionenvironment'

    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def put_execution_environment(self, execution_environment):
        # Store execution environment in etcd
        self.etcd_client.put(execution_environment.key(), execution_environment.value())

    def get_all_execution_environments(self):
        # Get all execution environments
        prefix = '/executionenvironment/'
        values = self.etcd_client.get_prefix(prefix)
        execution_environments = dict()
        for value, metadata in values:
            key = metadata.key.split('/')[-1]
            execution_environments[key] = ExecutionEnvironment.from_json(value)
        return execution_environments



