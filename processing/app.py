import connexion
from connexion import NoContent
import json
import os.path
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from flask_cors import CORS, cross_origin
import yaml
import logging
import logging.config


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
    
def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    if os.path.isfile(app_config['datastore']['filename']):  
        with open(app_config['datastore']['filename'], 'r') as f:
            data = f.read()
        log_data = json.loads(data)

    else:
        log_data = {
                "num_updates": 0, 
                "max_update_quantity": 0, 
                "num_orders": 0,
                "max_order_quantity": 0,
#                 "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                "last_updated": "2016-11-18 18:18:38.921052"
                }

    timestamp = log_data["last_updated"]
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    r_updates = requests.get(app_config['eventstore']['url'] + "/data/update?start_timestamp=" + timestamp + "&end_timestamp=" + current_timestamp)
    print(r_updates)
    updates_list = r_updates.json()
    print(updates_list)
    
    if r_updates.status_code != 200:
        logger.error("Received status code that was not 200")
    else:
        logger.info(f"Received {len(updates_list)} update events")
    
    r_orders = requests.get(app_config['eventstore']['url'] + "/data/order?start_timestamp=" + timestamp + "&end_timestamp=" + current_timestamp)
    print(r_orders)
    orders_list = r_orders.json()
    print(orders_list)
    
    if r_orders.status_code != 200:
        logger.error("Received status code that was not 200")
    else:
        logger.info(f"Received {len(orders_list)} order events")

    num_updates = log_data["num_updates"]
    num_updates += len(updates_list)
    max_update_quantity = log_data["max_update_quantity"]
    for event in updates_list:
        if event["quantity"] > max_update_quantity:
            max_update_quantity = event["quantity"]
    
    num_orders = log_data["num_orders"]
    num_orders += len(orders_list)
    max_order_quantity = log_data["max_order_quantity"]
    for event in orders_list:
        if event["quantity"] > max_order_quantity:
            max_order_quantity = event["quantity"]

    new_log = {
                "num_updates": num_updates, 
                "max_update_quantity": max_update_quantity, 
                "num_orders": num_orders,
                "max_order_quantity": max_order_quantity,
                "last_updated": current_timestamp
                }

    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(new_log, f, indent=2)

    logger.debug(f"{num_updates} update events and {num_orders} order events, with a max update quantity of {max_update_quantity} and max order quantity of {max_order_quantity} since {timestamp}.")
    logger.info("Period processing has concluded")

def get_stats():
    logger.info("Start retrieving stats")
    if os.path.isfile(app_config['datastore']['filename']):    
        with open(app_config['datastore']['filename'], 'r') as f:
            data = f.read()
        log_data = json.loads(data)
        logger.debug("Content of log file", log_data)

    else:
        logger.error("Statistics do not exist")
        return NoContent, 404

    logger.info("Request has been completed")
    return log_data, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                    'interval', 
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("ZCACIT3855-Inventory-API-1.0.0-swagger.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    """ Run our standalone gevent server """
    init_scheduler()
    app.run(port=8100, use_reloader=False)
