from os import name
import connexion
from connexion import NoContent
import json
import os.path
from datetime import datetime
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin
import yaml
import logging
import logging.config

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
# logger.info("Log COnf File: %s" % log_conf_file)

def get_update(index):
    """ Get Update in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)
    logger.info("Retrieving update at index %d" % index)
    try:
        event_counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg["type"] == "update" and event_counter == index:
                return msg, 200
            elif msg["type"] == "update":
                event_counter += 1 
    except:
        logger.error("No more messages found")

    logger.error("Could not find update at index %d" % index)
    return { "message": "Not Found"}, 404

def get_order(index):
    """ Get Order in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)
    logger.info("Retrieving order at index %d" % index)
    try:
        event_counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg["type"] == "order" and event_counter == index:
                return msg, 200
            elif msg["type"] == "order":
                event_counter += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find order at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("ZCACIT3855-Inventory-API-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8200)
