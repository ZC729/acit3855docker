import mysql.connector

_conn = mysql.connector.connect(host="acit3855-zchang.eastus.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          DROP TABLE inventory_updates, inventory_orders
          ''')

db_conn.commit()
db_conn.close()
