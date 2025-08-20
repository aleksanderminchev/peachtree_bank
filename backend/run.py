from app import create_app
from decouple import config

print('TEST RUN ')
app = create_app(config("CONFIG_NAME"))
