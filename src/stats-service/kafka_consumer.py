import time
import json
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient
from database import StatsDB
from datetime import datetime

BOOTSTRAP_SERVERS = 'kafka:9092'
TOPICS = ['post-events', 'post-interactions']

def wait_for_topics(bootstrap_servers, topics):
    admin = AdminClient({'bootstrap.servers': bootstrap_servers})
    start = time.time()
    while True:
        md = admin.list_topics(timeout=5)
        existing_topics = md.topics.keys()
        missing = [t for t in topics if t not in existing_topics]
        if not missing:
            print(f"All topics exist: {topics}", flush=True)
            return True
        print(f"Waiting for topics to be created: {missing}", flush=True)
        time.sleep(3)

def consume():
    if not wait_for_topics(BOOTSTRAP_SERVERS, TOPICS):
        print("Topics not available, exiting", flush=True)
        return

    db = StatsDB()
    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': 'stats-consumer',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(TOPICS)
    print("Subscribed to topics, starting consumption", flush=True)

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                print("Topic not yet available, waiting...", flush=True)
                time.sleep(5)
                continue
            print(f"Consumer error: {msg.error()}", flush=True)
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            event_type_map = {
                'post_viewed': 'view',
                'post_liked': 'like',
                'post_commented': 'comment'
            }
            event_type_raw = data.get("event_type")
            event_type = event_type_map.get(event_type_raw)

            if event_type is None:
                print(f"Unknown event_type: {event_type_raw}, skipping", flush=True)
                continue

            ts_str = data.get("timestamp")
            event_time = datetime.fromisoformat(ts_str) if ts_str else datetime.now()

            db.insert_event(
                event_time=event_time,
                post_id=int(data["post_id"]),
                user_id=int(data["user_id"]),
                event_type=event_type
            )
        except Exception as e:
            print(f"Failed to process message: {e}", flush=True)
