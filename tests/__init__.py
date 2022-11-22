import time
from datetime import datetime


def get_and_wait() -> datetime:
    time.sleep(0.000001)
    v = datetime.now()
    time.sleep(0.000001)
    return v
