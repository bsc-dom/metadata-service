import logging
import os
import socket

logger = logging.getLogger(__name__)


class Settings:

    # How many worker threads should be created/used by ThreadPoolExecutor
    THREAD_POOL_WORKERS = os.getenv("THREAD_POOL_WORKERS", default=None)

    SERVER_LISTEN_ADDR = "0.0.0.0"

    SERVER_LISTEN_PORT = int(os.getenv("METADATA_SERVICE_PORT_TCP", "16587"))

    ETCD_HOST = os.environ["ETCD_HOST"]
    ETCD_PORT = int(os.getenv("ETCD_PORT", "2379"))

    METADATA_SERVICE_HOST = os.getenv(
        "METADATA_SERVICE_HOST", socket.gethostbyname(socket.gethostname())
    )
    METADATA_SERVICE_PORT = int(os.getenv("METADATA_SERVICE_PORT", "16587"))


settings = Settings()
