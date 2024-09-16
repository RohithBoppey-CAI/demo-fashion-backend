from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker

# Connection details
print('connecting')
DATABASE_URL = "postgresql://rohithboppey:couture@127.0.0.1:5432/sampledb"

# Create a database engine
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

print('connected')

# Reflect existing database tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Create a new table (if it doesn't exist)
def create_table():
    print('in new table')
    new_table = Table(
        'new_table', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), nullable=False),
    )
    new_table.create(engine, checkfirst=True)  # Create table if it doesn't exist
    print("New table 'new_table' created.")

# Execute a SELECT query
def select_all_from_table(table_name):
    table = metadata.tables.get(table_name)
    if table is None:
        print(f"Table '{table_name}' does not exist.")
        return

    # Execute the SELECT * query
    query = table.select()

    with engine.connect() as connection:  # Use connection to execute queries
        result = connection.execute(query)

        # Fetch and print all rows
        for row in result:
            print(row)

if __name__ == "__main__":
    # Create the new table
    create_table()

    # Select data from an existing table
    table_name = "existing_table"  # Replace with your table name
    print(f"\nData from table '{table_name}':")
    select_all_from_table(table_name)

# Close the session
session.close()
