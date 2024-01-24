import pandas as pd
from pymongo import MongoClient

# It will create a new Database named 'Warehouse'
mongodb_uri = 'mongodb://localhost:27017/'
client = MongoClient(mongodb_uri)
db = client['Warehouse']

# Store every table in a new collection
def load_data_to_database(tableNames):
    for table in tableNames:
        csv_file_path = f'{table}.csv'
        collection_name = table

        df = pd.read_csv(csv_file_path)
        data = df.to_dict(orient='records')
        collection = db[collection_name]

        collection.insert_many(data)

        print(f"CSV file '{csv_file_path}' successfully loaded into MongoDB collection '{collection_name}' in database 'Warehouse'.")


if __name__ == "__main__":
    tableNames = ['MetaData', 'Tags', 'PriceAndRating', 'UserDetail', 'Reviews']
    load_data_to_database(tableNames)

client.close()