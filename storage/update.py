from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Update(Base):
    """ Update """

    __tablename__ = "inventory_updates"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(250), nullable=False)
    manufacturer_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __init__(self, manufacturer_id, product_id, name, quantity):
        """ Initializes a Update reading """
        self.manufacturer_id = manufacturer_id
        self.product_id = product_id
        self.name = name
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.quantity = quantity

    def to_dict(self):
        """ Dictionary Representation of a Update reading """
        dict = {}
        dict['id'] = self.id
        dict['manufacturer_id'] = self.manufacturer_id
        dict['product_id'] = self.product_id
        dict['name'] = self.name
        dict['Update'] = {}
        dict['quantity'] = self.quantity
        dict['date_created'] = self.date_created

        return dict