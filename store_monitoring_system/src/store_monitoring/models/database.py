from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    face_encoding = Column(String)
    last_seen = Column(DateTime)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sku = Column(String, unique=True)
    price = Column(Float)

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    aisle_id = Column(String)
    product = relationship("Product")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    customer = relationship("Customer")
    product = relationship("Product")

class Planogram(Base):
    __tablename__ = 'planograms'
    id = Column(Integer, primary_key=True)
    aisle_id = Column(String)
    product_id = Column(Integer, ForeignKey('products.id'))
    position_x = Column(Integer)
    position_y = Column(Integer)
    product = relationship("Product")