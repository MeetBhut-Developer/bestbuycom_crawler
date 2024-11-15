import sqlite3
import json
import os

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"connection err: {e}")
            raise

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()

class BestBuyDataFetcher:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_data(self, start_time, end_time):
        """
        Fetch data from 'products_2024_11_14' table based on the timestamp range and join with 'master_products'.

        :param start_time: Start time in 'YYYY-MM-DD HH:MM:SS' format.
        :param end_time: End time in 'YYYY-MM-DD HH:MM:SS' format.
        :return: List of JSON objects.
        """
        query = """
            SELECT mp.product_name, mp.description, p.price, p.availability, p.discount, p.rating_value,
                   p.review_count, p.reviewer_1, p.reviewer_2, p.reviewer_3
            FROM products_2024_11_14 p
            JOIN master_products mp ON p.product_id = mp.product_id
            WHERE p.timestamp BETWEEN ? AND ?
        """
        rows = self.db_connection.execute_query(query, (start_time, end_time))

        return self._format_data(rows)

    def _format_data(self, rows):
        
        formatted_data = []
        for row in rows:
            product_data = {
                "productName": row[0],
                "description": row[1],
                "price": str(row[2]),
                "discount": str(row[4]),
                "availability": row[3],
                "reviews": row[6],
                "stars": str(row[5]),
                "topReviews": [
                    json.loads(row[7]) if row[7] else [],
                    json.loads(row[8]) if row[8] else [],
                    json.loads(row[9]) if row[9] else []
                ]
            }
            formatted_data.append(product_data)

        return formatted_data

def main():
    # Set up paths and database connection
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '..', 'database', 'bestbuy.db')
    db_path = os.path.abspath(db_path)

    # Establish database connection
    db_connection = DatabaseConnection(db_path)

    # Instantiate the data fetcher
    fetcher = BestBuyDataFetcher(db_connection)

    # Define time period
    start_time = "2024-11-15 08:00:00"
    end_time = "2024-11-15 09:00:00"

    # Fetch data
    data = fetcher.fetch_data(start_time, end_time)

    # Print results in JSON format
    if data:
        print(json.dumps(data, indent=4))
    else:
        print(f"No data found between {start_time} and {end_time}.")

    # Close database connection
    db_connection.close()

if __name__ == "__main__":
    main()
