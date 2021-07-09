from persist.hl7batch_tracking_dao import HL7BatchTrackingDao

# See the integration_tests/integration_test_hl7batch_tracking_dao tests for testing the HL7BatchTrackingDao.
# Without a database connection there isn't much to unittest.
# If we need to test some more complicated logic in the future we can add tests here.


def test_HL7BatchTrackingDao():
    dao = HL7BatchTrackingDao()
    return dao
