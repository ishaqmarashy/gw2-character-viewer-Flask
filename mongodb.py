
from pymongo import MongoClient
import os
import pymongo
from dotenv import load_dotenv
load_dotenv()
# gw2stuff=NULL
def get_database():
    # CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/myFirstDatabase"
    CONNECTION_STRING= os.environ["CONNECTION_STRING"]

     # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['gw2stuff']

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    # Get the database
    dbname = get_database()
    
