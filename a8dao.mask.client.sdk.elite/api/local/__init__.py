from config import config

local_config = config["api"]["local"]
host = local_config["host"]
headers = {"Content-Type": "application/json"}
