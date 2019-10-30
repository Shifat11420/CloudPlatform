import threading
import time
import sys
import random

def run():
    while True:
        time.sleep(1)
        for i in range(100):
            for j in range(100):
                x = random.uniform(10,100)
                y = random.uniform(30,70)
                z = x * y


if __name__ == "__main__":
    run()
