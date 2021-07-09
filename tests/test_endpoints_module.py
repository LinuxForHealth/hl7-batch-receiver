"""
Purpose: Test endpoints_module.py
"""

import pytest
from fastapi.exceptions import HTTPException
from fastapi.datastructures import UploadFile
from persist.hl7batch_tracking_dao import HL7BatchTrackingDao
from persist.minio import PersistMinio
from src.rest.endpoints_module import ping, upload_hl7_batchzip


def _mock_init_client():
    pass


def _mock_upload_object():
    return "response"


def testPing():
    response_text = next(iter(ping()))
    assert "Pong" in response_text


@pytest.mark.asyncio
async def test_upload_batch_fails_no_zip(mocker):
    mocker.patch.object(PersistMinio, "init_client")
    with pytest.raises(HTTPException):
        test_batchzip = open("./tests/data_for_test/testWith3Files.zip", "rb")
        f = UploadFile("", test_batchzip, "")
        await upload_hl7_batchzip(f, "test")


@pytest.mark.asyncio
async def test_upload_batch(mocker):
    mocker.patch.object(HL7BatchTrackingDao, "init_pool")
    mocker.patch.object(HL7BatchTrackingDao, "insert_new_batch")
    mocker.patch.object(HL7BatchTrackingDao, "update_hl7batch_with_storage_id")

    mocker.patch.object(PersistMinio, "init_client")
    mock_minio_upload = mocker.patch.object(PersistMinio, "upload_batch")
    mock_kafka_call = mocker.patch(
        "src.rest.endpoints_module._send_kafka_topic", return_value="sent"
    )

    test_batchzip = open("./tests/data_for_test/testWith3Files.zip", "rb")
    f = UploadFile("", test_batchzip, "some-zip-content")
    await upload_hl7_batchzip(f, "test")

    HL7BatchTrackingDao.insert_new_batch.assert_called_once()
    HL7BatchTrackingDao.update_hl7batch_with_storage_id.assert_called_once()
    mock_minio_upload.assert_called_once()
    mock_kafka_call.assert_called_once()

