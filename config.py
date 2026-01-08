import os


server_domain = os.environ['SERVER_DOMAIN']
dnevnik_client_id = os.environ['DNEVNIK_CLIENT_ID']

db_config = {
    'host': os.environ['DBHOST'],
    'user': os.environ['DBUSER'],
    'password': os.environ['DBPASS'],
    'database': os.environ['DBNAME']
}
