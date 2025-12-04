import os


server_domain = os.environ['SERVER_DOMAIN']

db_config = {
    'host': os.environ['DBHOST'],
    'user': os.environ['DBUSER'],
    'password': os.environ['DBPASS'],
    'database': os.environ['DBNAME']
}

no_lessons = (2413391233457798343, 2413391078838975686)
gymnasium_id = os.environ['GYMNASIUM_ID']
dnevnik_client_id = os.environ['DNEVNIK_CLIENT_ID']
