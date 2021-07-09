"""
Purpose: hl7 batch receiver rest API endpoints associated with the project.yaml file.
"""
from persist.hl7batch_tracking_dao import HL7BatchTrackingDao
from persist.minio import PersistMinio
from datetime import datetime
from transmit.producer import get_producer
from typing import Optional
from fastapi import HTTPException, Header, File, UploadFile
from kafka import errors
from util import hl7_batch_logger, config
import io
import traceback


logger = hl7_batch_logger.get_logger(__name__)

_DATE_FORMAT = "%Y-%m-%d_%I-%M-%S"
STORAGE_WRITE_ERROR = "Error while persisting HL7 batch."

cfg = config.get_config()

logger.info(
    f"Hl7 batch service with configuration: {', '.join([f'{k}={v}' for k, v in cfg.items()])}"
)

BOOTSTRAP_SERVERS = cfg["kafka"]["BOOTSTRAP_SERVERS"]
TOPIC_NAME = cfg["kafka"]["TOPIC"]


# TODO: This isn't great. There's probably a good way to do this with Fast API, but changes would be required
#       to the py-wrapper-service.
# See: https://github.com/tiangolo/fastapi/issues/1800 for more info
batch_dao = HL7BatchTrackingDao()

minio_client = PersistMinio()


def _verify_tenant_id(tenant_id: str):
    """ Utility to verify tenant id provide and throw exception if not. """
    if not tenant_id:
        logger.error("'tenant-id' header not provided.")
        raise HTTPException(
            status_code=412, detail="The 'tenant-id' request header is required."
        )


async def _send_kafka_topic(tenant_id: str, object_name: str, batch_id: str):
    """
    Get Kafka producer and send kafka topic with a reference to the filepath.
    Raise an HTTPException if errors occur and roll back the file creation.
    """

    notification = {
        "userMetadata": {
            "X-Amz-Meta-storageid": object_name,
            "X-Amz-Meta-batchid": batch_id,
            "Z-Amz-Meta-tenantid": tenant_id,
        }
    }

    try:
        producer = get_producer(BOOTSTRAP_SERVERS)
    except errors.KafkaError as re:
        logger.error("Error while connecting to kafka")
        raise HTTPException(status_code=500, detail=str(re))

    try:
        future = producer.send(
            TOPIC_NAME, value=notification, headers=[("tenant-id", tenant_id.encode())],
        )

        # producer is async by default, following statement makes it blocking
        future.get(timeout=10)

    except RuntimeError as r:
        logger.error("Error while sending to kafka deleting batch..." + str(r))
        await minio_client.delete_batch(bucket_name=tenant_id, object_name=object_name)
        raise HTTPException(
            status_code=500, detail="Cannot send to kafka, write has been rolled back"
        )


# Simple API to verify the service is running.
def ping():
    return {"Pong - the hl7 batch receiver service is running."}


async def upload_hl7_batchzip(
    file: UploadFile = File(...), tenant_id: Optional[str] = Header(None)
):

    minio_client.init_client(
        cfg["minio"]["MINIO_ENDPOINT"],
        cfg["minio"]["MINIO_ROOT_USER"],
        cfg["minio"]["MINIO_ROOT_PASSWORD"],
    )
    _verify_tenant_id(tenant_id)

    # Wait for the async operation to read the contents.
    file_bytes = await file.read()

    # timestamp to attach to object name
    timestamp = datetime.now().strftime(_DATE_FORMAT)

    # The bucket name derivable from tenant_id
    bucket_name = tenant_id

    try:

        # TODO: have to init the pool here until we can integrate the db connection into the fast API middleware
        await batch_dao.init_pool()
        hl7batch_id = await batch_dao.insert_new_batch(tenant_id)
        logger.debug(
            f"Created new batch tracking entry with hl7batch_id: {hl7batch_id}"
        )

        # creating object name within bucket, this will be storageid
        object_name = f"{timestamp}-{hl7batch_id}-{file.filename}"

        if "zip" not in file.filename:
            object_name = object_name + "hl7batch.zip"

        await minio_client.upload_batch(
            bucket_name, object_name, io.BytesIO(file_bytes)
        )

        await batch_dao.update_hl7batch_with_storage_id(object_name, hl7batch_id)
        logger.debug(
            f"Updated new batch tracking entry (hl7batch_id: {hl7batch_id}) with storage_id: {object_name}"
        )

    except Exception as e:
        logger.error(STORAGE_WRITE_ERROR)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=STORAGE_WRITE_ERROR + str(e))

    await _send_kafka_topic(tenant_id, object_name, hl7batch_id)

    return {"Received file named": file.filename}


if __name__ == "__main__":
    pass
