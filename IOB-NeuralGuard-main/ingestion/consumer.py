from kafka import KafkaConsumer
from config.settings import settings
from ingestion.schemas import Transaction
from core.logger import get_logger
import json

logger = get_logger(__name__)

def run_consumer():
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='fraud-detection-group'
    )
    logger.info(f'Listening on topic: {settings.kafka_topic}...')
    for message in consumer:
        try:
            payload = message.value.decode('utf-8')
            txn = Transaction.model_validate_json(payload)
            logger.info(f'Received Valid Txn: {txn.txn_id} from {txn.sender_upi}')
        except Exception as e:
            logger.error(f'Failed to process message: {e} | Raw: {message.value}')

if __name__ == '__main__':
    run_consumer()
