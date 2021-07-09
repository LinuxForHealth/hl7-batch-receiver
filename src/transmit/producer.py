from kafka import KafkaProducer
from util import hl7_batch_logger
import json

logger = hl7_batch_logger.get_logger(__name__)
_producer = None


def get_producer(servers):
    global _producer
    if _producer is None:
        # logger.info("Creating instance of KafkaProducer")
        _producer = KafkaProducer(
            bootstrap_servers=servers,
            acks="all",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return _producer
