import pytest
from persist.hl7batch_tracking_dao import HL7BatchTrackingDao


# These tests require supporting services to be running (postgres).
# See readme for information on how to setup those services locally.


@pytest.fixture
async def batch_dao():
    # NOTE: Due to some limitation of the postgres-lib, configuration environment variables that allow
    # use of local postgres are set in the gradle file cdpHl7IntegrationBatchTest task.
    batch_dao = HL7BatchTrackingDao()
    await batch_dao.init_pool()
    return batch_dao


@pytest.mark.asyncio
async def test_insert(batch_dao):
    test_tenant_id = "test_insert_tenant_1"
    res = await batch_dao.insert_new_batch(test_tenant_id)
    assert res is not None


@pytest.mark.asyncio
async def test_update(batch_dao):
    test_tenant_id = "test_update_tenant_2"
    hl7batch_id = await batch_dao.insert_new_batch(test_tenant_id)
    test_storage_id = "test_update_storage_id"
    await batch_dao.update_hl7batch_with_storage_id(test_storage_id, hl7batch_id)
