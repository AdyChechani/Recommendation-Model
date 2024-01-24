import csv
from datetime import date
from pymongo import MongoClient

# MongoDB connection settings
mongo_uri = 'mongodb://localhost:27017/Source' # connection string
mongo_collection = 'Data' # collection name

# Output CSV file
csv_file_path = f"extracted_data_{date.today()}.csv"

# Connect to MongoDB
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client.get_database()
collection = mongo_db.get_collection(mongo_collection)

def fetch_data_and_write_to_csv():
    # Fetch data from MongoDB
    cursor = collection.find()

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        header_written = False

        for document in cursor:
            if not header_written:
                csv_writer.writerow(document.keys())
                header_written = True

            csv_writer.writerow(document.values())


if __name__ == "__main__":
    fetch_data_and_write_to_csv()

mongo_client.close()