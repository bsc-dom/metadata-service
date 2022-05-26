import logging

from dataclay_mds.server.metadata_service_srv import MetadataServiceSrv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_main():
    logger.info("Start Metadata Service")
    MetadataServiceSrv().start()

if __name__ == "__main__":
    run_main()