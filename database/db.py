import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():

    connection = mysql.connector.connect(
        host=os.getenv("localhost"),
        user=os.getenv("root"),
        password=os.getenv("Apkae1098!@$"),
        database=os.getenv("resume_analyzer")
    )

    return connection