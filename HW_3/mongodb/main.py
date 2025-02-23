import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

# Load environment variables from the .env file
load_dotenv()

# Take the URI from the .env file
MONGO_URI = os.getenv("MONGO_URI")

def get_db():
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    db = client.pets  # The database's name
    collection = db.cats  # The collection's name
    return collection

def read_all_cats():
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    cats = list(collection.find())

    if cats:
        for cat in cats:
            print(cat)
    else:
        print("No cats found.")

def read_cat_by_name(name):
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    cat = collection.find_one({"name": name})

    if cat:
        print(cat)
    else:
        print("Cat not found.")

def update_age(name, new_age):
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    result = collection.update_one({"name":name}, {"$set": {"age": new_age}})
    if result.modified_count:
        print("Age updated successfully.")
    else:
        print("Cat not found.")

def add_feature(name, feature):
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    result = collection.update_one({"name":name}, {"$push": {"features": feature}})
    if result.modified_count:
        print("Feature added successfully.")
    else:
        print("Cat not found.")

def delete_cat_by_name(name):
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    result = collection.delete_one({"name": name})
    if result.deleted_count:
        print("Cat deleted successfully.")
    else:
        print("Cat not found.")

def delete_cats_all():
    collection = get_db()
    if collection is None:
        print("Error! Could not connect to the `hw3` database.")
        return
    result = collection.delete_many({})
    if result.deleted_count:
        print("All cats deleted successfully.")
    else:
        print("No cats found.")


if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1. Read all cats")
        print("2. Read cat by name")
        print("3. Update cat's age")
        print("4. Add feature to cat")
        print("5. Delete cat by name")
        print("6. Delete all cats")
        print("7. Exit")

        choice = input("Choose an option:")

        if choice == "1":
            read_all_cats()
        elif choice == "2":
            name = input("Enter cat's name:")
            read_cat_by_name(name)
        elif choice == "3":
            name = input("Enter cat's name:")
            new_age = input("Enter new age:")
            update_age(name, new_age)
        elif choice == "4":
            name = input("Enter cat's name:")
            feature = input("Enter feature:")
            add_feature(name, feature)
        elif choice == "5":
            name = input("Enter cat's name:")
            delete_cat_by_name(name)
        elif choice == "6":
            delete_cats_all()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")
