import connexion
from connexion import NoContent
import json
import os.path
import requests
import logging
import logging.config
import yaml
import datetime
from pykafka import KafkaClient
import time


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

max_tries = app_config["events"]["max_retries"]
num_attempts = 0
hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
while num_attempts <= max_tries:
    logger.info("Trying to connect to Kafka: Current retry count " + str(attempts))
    try:
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
    except:
        logger.error("Attempted Kafka connection failed")
        time.sleep(app_config["events"]["sleep_time"])
        num_attempts += 1

def update_inventory(body):
    """Receives an inventory update event"""
    # print(app_config['eventstore1']['url'])
    logger.log(logging.INFO, f"Received event 'update_inventory' request with a unique id of {body['manufacturer_id']}")

    # Handle the request here
    headers = {"content-type": "application/json"}
    
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])# response = requests.post(str(app_config['eventstore1']['url']), json=body, headers=headers)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "update",
            "datetime" :
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
                "payload":  body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.log(logging.INFO, f"Returned event 'update_inventory' response {body['manufacturer_id']} with status 201")

    return NoContent, 201

def create_order(body):
    """Receives a create order event"""
    # print(str(app_config['eventstore2']['url']))
    logger.log(logging.INFO, f"Received event 'create_order' request with a unique id of {body['customer_id']}")

    # Handle the request here
    headers = {"content-type": "application/json"}
    # response = requests.post(str(app_config['eventstore2']['url']), json=body, headers=headers)
# response = requests.post(str(app_config['eventstore1']['url']), json=body, headers=headers)
#     client = KafkaClient(hosts=hostname)
#     topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "order",
            "datetime" :
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
                "payload":  body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.log(logging.INFO, f"Returned event 'create order' response {body['customer_id']} with status 201")

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("ZCACIT3855-Inventory-API-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
