from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from databases import Database
import models
from models import Customer, Order, OrderItem, Product  


DATABASE_URL = "postgresql://rohithboppey:couture@localhost:5432/sampledb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database = Database(DATABASE_URL)


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# # Pydantic model for request validation
# class UserCreate(BaseModel):
#     name: str
#     email: str
# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL!"}

@app.get("/all_top_5")
async def top_5(db: Session = Depends(get_db)):
    customer_spending_subquery = (
        db.query(
            Customer.customer_id,
            Customer.customer_name,
            Customer.email,
            Product.category,
            func.sum(OrderItem.quantity * OrderItem.price_per_unit).label("total_spent_in_category")
        )
        .join(Order, Customer.customer_id == Order.customer_id)
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .group_by(Customer.customer_id, Customer.customer_name, Customer.email, Product.category)
        .subquery()
    )
    print(customer_spending_subquery)


    # total spending per customer
    total_spending_subquery = (
        db.query(
            customer_spending_subquery.c.customer_id,
            customer_spending_subquery.c.customer_name,
            customer_spending_subquery.c.email,
            func.sum(customer_spending_subquery.c.total_spent_in_category).label("total_spent")
        )
        .group_by(customer_spending_subquery.c.customer_id, customer_spending_subquery.c.customer_name, customer_spending_subquery.c.email)
        .subquery()
    )
    print(total_spending_subquery)


    # category with the maximum spending for each customer
    most_purchased_category_subquery = (
        db.query(
            customer_spending_subquery.c.customer_id,
            customer_spending_subquery.c.category.label("most_purchased_category"),
            customer_spending_subquery.c.total_spent_in_category
        )
        .distinct(customer_spending_subquery.c.customer_id)
        .order_by(customer_spending_subquery.c.customer_id, desc(customer_spending_subquery.c.total_spent_in_category))
        .subquery()
    )
    print(most_purchased_category_subquery)

    # top 5 customers with their total spending and most purchased category
    top_5_customers = (
        db.query(
            total_spending_subquery.c.customer_id,
            total_spending_subquery.c.customer_name,
            total_spending_subquery.c.email,
            total_spending_subquery.c.total_spent,
            most_purchased_category_subquery.c.most_purchased_category
        )
        .join(
            most_purchased_category_subquery,
            total_spending_subquery.c.customer_id == most_purchased_category_subquery.c.customer_id
        )
        .order_by(desc(total_spending_subquery.c.total_spent))
        .limit(5)
        .all()
    )
    print(top_5_customers)
    
    
    # we need to convert into JSON, so dict
    result = []
    for customer in top_5_customers:
        customer_dict = {
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name,
            "email": customer.email,
            "total_spent": customer.total_spent,
            "most_purchased_category": customer.most_purchased_category
        }
        result.append(customer_dict)

    return result


@app.on_event("startup")
async def startup():
    await database.connect()
    print('connected to database')

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
