from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    signup_date = Column(Date, nullable=False)
    
    orders = relationship('Order', back_populates='customer')

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    order_date = Column(Date, nullable=False)
    total_amount = Column(DECIMAL, nullable=False)
    
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_id = Column(String, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(DECIMAL, nullable=False)
    
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    
    order_items = relationship('OrderItem', back_populates='product')

