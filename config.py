import os


server_domain = os.environ['SERVER_DOMAIN']

db_config = {
    'host': os.environ['DBHOST'],
    'user': os.environ['DBUSER'],
    'password': os.environ['DBPASS'],
    'database': os.environ['DBNAME']
}

gymnasium_id = os.environ['GYMNASIUM_ID']
dnevnik_client_id = os.environ['DNEVNIK_CLIENT_ID']
