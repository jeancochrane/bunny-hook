from api.queue import Queue
import time


if __name__ == '__main__':
    queue = Queue()

    # Run the queue in an endless loop
    while True:
        queue.run()
        time.sleep(0.01)
