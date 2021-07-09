from util import hl7_batch_logger

from whpa_cdp_postgres import postgres
from persist.db_batch_status_enum import BatchStatus

logger = hl7_batch_logger.get_logger(__name__)

# This needs to match the schema
BATCH_ID_COLLUMN_NAME = "hl7batch_id"


# Database Access Object for the hl7batch table used to track the processing of HL7 batches
class HL7BatchTrackingDao:
    def __init__(self):
        self._postgres = None

    async def init_pool(self):

        if self._postgres is None:
            self._postgres = await postgres.create_postgres_pool(
                config_section="postgres"
            )

    # Inserts a new row to hl7Batch with status recieved to denote receipt of an hl7Batch notification
    # Returns the batch_id of the inserted record.
    async def insert_new_batch(self, tenant_id):

        result = None

        result = await self._postgres.fetch(
            """
            INSERT INTO cdp_orch.hl7batch (tenant_id, hl7batch_status) values ($1, $2) RETURNING hl7batch_id
            """,
            tenant_id,
            BatchStatus.RECIEVED.value,
        )

        return result[0][BATCH_ID_COLLUMN_NAME]

    # Update hl7Batch with storage ID
    async def update_hl7batch_with_storage_id(self, storage_id, hl7batch_id):

        await self._postgres.execute(
            """
            UPDATE cdp_orch.hl7batch SET hl7batch_storage_id = $1, hl7batch_status = $2 WHERE hl7batch_id = $3
            """,
            storage_id,
            BatchStatus.IN_PROGRESS.value,
            hl7batch_id,
        )
