import os

raw_env = ['='.join([key, value]) for key, value in os.environ.items()]
bind = '0.0.0.0:8000'
max_requests = 1000
workers = 4
