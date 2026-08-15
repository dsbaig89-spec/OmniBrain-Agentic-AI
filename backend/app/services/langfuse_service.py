from dotenv import load_dotenv
from langfuse import get_client

load_dotenv("backend/.env")

langfuse = get_client()