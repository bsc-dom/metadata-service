
import logging
import os

logger = logging.getLogger(__name__)

class Settings:

    # How many worker threads should be created/used by ThreadPoolExecutor
    THREAD_POOL_WORKERS = os.getenv("THREAD_POOL_WORKERS", default=None)


    SERVER_LISTEN_ADDR = "0.0.0.0"

    SERVER_LISTEN_PORT = int(os.getenv("METADATA_SERVICE_PORT_TCP", "16587"))

    ETCD_HOST = os.getenv("ETCD_HOST", "127.0.0.1")
    ETCD_PORT = int(os.getenv("ETCD_PORT", "2379"))

    

    

settings = Settings()
