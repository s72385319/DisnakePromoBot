import os
import disnake
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN") #Token bota
OWNER_IDS = [1089855889038639164] #id Владельца

Success = disnake.Color.green
Error = disnake.Color.red
Random = disnake.Color.random
