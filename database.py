import psycopg2
from psycopg2 import sql, errors

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_url = "dbname=lab_db user=lab_test password=lab_test host=localhost port=5433"

    def open_connection(self):
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.cursor = self.connection.cursor()
            print("Успешное подключение")
        except errors.OperationalError as e:
            print(f"Ошибка при подключении: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None