import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from datetime import date
from random import randint, choice
from decimal import Decimal
from models import Customer, Order, OrderItem, Product  
from databases import Database

def generate_orders_from_csv(csv_file, session):
    # Open the CSV file
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        
        for index, row in enumerate(reader):
            # Creating or fetching a random customer
            customer = generate_or_get_customer(session)
            
             # Create or update the product
            product = session.query(Product).filter_by(product_id=row['product_id']).first()
            if not product:
                product = Product(
                    product_id=row['product_id'],
                    product_name=row['product_name'],
                    category=row['category']
                )
                session.add(product)

            # Create an order
            order = Order(
                customer_id=customer.customer_id,
                order_date=date.today(),
                total_amount=Decimal(row['price']) * Decimal(row['quantity_sold'])
            )
            session.add(order)
            session.flush()  # Flush to get order_id for OrderItems
            
            # Create an order item
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=row['product_id'],
                quantity=int(row['quantity_sold']),
                price_per_unit=Decimal(row['price'])
            )
            session.add(order_item)
            
        # Commit after processing all rows
        session.commit()

def generate_or_get_customer(session):
    # Generate a random customer for simplicity
    customer_name = f"Customer_{randint(1, 9)}"
    email = f"{customer_name.lower()}@example.com"
    customer = session.query(Customer).filter_by(email=email).first()
    
    if not customer:
        customer = Customer(
            customer_name=customer_name,
            email=email,
            signup_date=date.today()
        )
        session.add(customer)
        session.flush()  # Flush to get customer_id
    
    return customer

# PostgreSQL database URL
DATABASE_URL = "postgresql://rohithboppey:couture@localhost:5432/sampledb"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Database setup for non-blocking queries
database = Database(DATABASE_URL)

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

# Call function with CSV file
csv_file = './data/processed.csv'
generate_orders_from_csv(csv_file, session)
