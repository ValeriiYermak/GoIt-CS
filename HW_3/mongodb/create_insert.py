import os
import random
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from faker import Faker

# Load environment variables from the .env file
load_dotenv()

# Take the URI from the .env file
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client.pets # The database's name
collection = db.cats # The collection's name

#Create a Faker instance
fake = Faker()

# The features list of cats
cat_features = ["ходить в капці", "дає себе гладити", "рудий", "грається з мотузкою", "любить їсти рибу",
    "спить на ноутбуці", "ховається під ковдрою", "муркоче голосно", "боїться пилососа", "сірий"]


cats = []
# Generate 10 random cat documents
for _ in range(10): # The number of documents to generate
    cat = {
        "name": fake.first_name().lower(),
        "age": random.randint(1, 15),
        "features": random.sample(cat_features, k=random.randint(1, 4))
    }
    cats.append(cat)

# Print the generated documents
for cat in cats:
    print(cat)

# Insert the generated documents into the collection

result = collection.insert_many(cats)

print("The data was inserted successfully!")
print("Inserted IDs:", result.inserted_ids)
