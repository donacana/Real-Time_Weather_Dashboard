import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / '.env')
def env(key, default=''):
    return os.environ.get(key, default)
