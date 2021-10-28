from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Order(Base):
    """ Order """

    __tablename__ = "inventory_orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    product_id = Column(String(250), nullable=False)
    date = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __init__(self, customer_id, product_id, date, quantity):
        """ Initializes a Order reading """
        self.customer_id = customer_id
        self.product_id = product_id
        self.date = date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.quantity = quantity

    def to_dict(self):
        """ Dictionary Representation of a Order reading """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['product_id'] = self.product_id
        dict['order'] = {}
        dict['quantity'] = self.quantity
        dict['date'] = self.date
        dict['date_created'] = self.date_created

        return dict