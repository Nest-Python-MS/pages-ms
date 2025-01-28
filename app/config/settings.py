from dotenv import load_dotenv
import os

load_dotenv()

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
