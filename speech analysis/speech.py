from dotenv import load_dotenv
from pathlib import Path
env_path = Path('../../../.env') # Change with your .env file
load_dotenv(dotenv_path=env_path,override=True)