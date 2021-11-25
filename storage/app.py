import connexion
from connexion import NoContent
import json
import os.path
import sqlalchemy
from sqlalchemy import and_
from datetime import datetime
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import time

import pymysql
import yaml
import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from order import Order
from update import Update

# if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
#     print("In Test Environment")
#     app_conf_file = "/config/app_conf.yml"
#     log_conf_file = "/config/log_conf.yml"
# else:
#     print("In Dev Environment")
app_conf_file = "app_conf.yml"
log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# logger.info("App Conf File: %s" % app_conf_file)
# logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def update_inventory(body):
    """Receives an inventory update event"""

    session = DB_SESSION()

    update = Update(body['manufacturer_id'],
                       body['product_id'], 
                       body['name'],
                       body['quantity'])

    session.add(update)

    session.commit()
    session.close()

    logger.log(logging.DEBUG, f"Stored event 'update_inventory' request with a unique id of {body['manufacturer_id']}")

    return NoContent, 201

def create_order(body):
    """Receives a create order event"""
    session = DB_SESSION()
    order = Order(body['customer_id'],
                       body['product_id'],
                       body['date'],
                       body['quantity'])
    session.add(order)
    session.commit()
    session.close()

    logger.log(logging.DEBUG, f"Stored event 'create_order' request with a unique id of {body['customer_id']}")

    return NoContent, 201

def get_inventory_updates(start_timestamp, end_timestamp):
    """ Gets new inventory updates after the timestamp"""

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

    inventory_updates = session.query(Update).filter(and_(Update.date_created >= start_timestamp_datetime, Update.date_created < end_timestamp_datetime))

    results_list = []

    for inventory_update in inventory_updates:
        results_list.append(inventory_update.to_dict())

    session.close()

    logger.info("Query for Inventory Update events after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200

def get_inventory_orders(start_timestamp, end_timestamp):
    """ Gets new inventory orders after the timestamp"""

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

    inventory_orders = session.query(Order).filter(and_(Order.date_created >= start_timestamp_datetime, Order.date_created < end_timestamp_datetime))


    results_list = []

    for inventory_order in inventory_orders:
        results_list.append(inventory_order.to_dict())

    session.close()

    logger.info("Query for Inventory Order events after %s returns %d results" % (start_timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    max_tries = app_config["events"]["max_retries"]
    num_attempts = 0
    logger.info("Attempting to connect to Kafka")
    while num_attempts <= max_tries:
        try:
            logger.info("Attempt %s to connect to Kafka" % (num_attempts))
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            logger.info("Successfully connected to Kafka")
            break
        except:
            logger.error("Attempted Kafka connection failed")
            time.sleep(app_config["events"]["sleep_time"])
            num_attempts += 1
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
 # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        payload = msg["payload"]
        
        if msg["type"] == "update": # Change this to your event type
            update_inventory(payload)
            # Store the event1 (i.e., the payload) to the DB
        elif msg["type"] == "order": # Change this to your event type
            create_order(payload)
            # Store the event2 (i.e., the payload) to the DB
            # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("ZCACIT3855-Inventory-API-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logger.info(f"Connecting to DB: {app_config['datastore']['hostname']} Port: {app_config['datastore']['port']}")
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
