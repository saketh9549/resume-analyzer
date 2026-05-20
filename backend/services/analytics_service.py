from database.db import get_connection
import pandas as pd

def get_skill_data():

    connection = get_connection()

    query = """
    SELECT
        skill_name,
        COUNT(*) as count
    FROM resume_skills
    GROUP BY skill_name
    """

    df = pd.read_sql(query, connection)

    connection.close()

    return df