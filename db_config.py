import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname='inventario_db',
        user='postgres',
        password='1020',
        host='localhost',
        port='5432',
    )
