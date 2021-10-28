import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-zchang.eastus.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE inventory_orders
          (id INTEGER NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           product_id VARCHAR(250) NOT NULL,
           quantity INTEGER NOT NULL,
           date VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT order_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE inventory_updates
          (id INTEGER NOT NULL AUTO_INCREMENT, 
           manufacturer_id VARCHAR(250) NOT NULL,
           product_id VARCHAR(250) NOT NULL,
           name VARCHAR(250) NOT NULL,
           quantity INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT update_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
