import os
from dotenv import load_dotenv

load_dotenv()

DSN = os.getenv("DSN")
TOKEN_BOT = os.getenv("TOKEN_BOT")
TOKEN_API_VK = os.getenv("TOKEN_API_VK")
GROUP_ID = os.getenv("GROUP_ID")
VERSION_API_VK = os.getenv("VERSION_API_VK")
ID_APP = os.getenv("ID_APP")
