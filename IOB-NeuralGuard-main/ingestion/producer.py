import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer
from config.settings import settings
from ingestion.schemas import Transaction
from core.logger import get_logger

logger = get_logger(__name__)

UPI_IDS = [
    'user1@okhdfcbank', 'user2@okaxis', 'user3@paytm', 'user4@ybl', 'user5@ibl',
    'merchantA@business', 'merchantB@shop', 'store1@pay', 'vendorX@upi', 'charity@org'
]

def get_random_transaction():
    sender = random.choice(UPI_IDS)
    receiver = random.choice([u for u in UPI_IDS if u != sender])
    amount = round(random.uniform(100, 50000), 2)
    is_voice = random.random() < 0.20
    channel = 'VOICE_123PAY' if is_voice else 'UPI'
    return Transaction(
        txn_id=str(uuid.uuid4()),
        sender_upi=sender,
        receiver_upi=receiver,
        amount=amount,
        timestamp=datetime.now(),
        channel=channel,
        audio_ref=f'audio_{uuid.uuid4()}.wav' if is_voice else None
    )

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info(f'Starting producer on topic: {settings.kafka_topic}')
    try:
        while True:
            txn = get_random_transaction()
            producer.send(settings.kafka_topic, txn.model_dump(mode='json'))
            logger.info(f'Sent txn: {txn.txn_id} | Amount: {txn.amount} | Channel: {txn.channel}')
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping producer...')
    except Exception as e:
        logger.error(f'Producer failed: {e}')
    finally:
        producer.close()

if __name__ == '__main__':
    run_producer()
