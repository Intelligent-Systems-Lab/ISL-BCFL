import threading


def create_job(worker, args=()):
    t = threading.Thread(target=worker, args=args)
    t.start()
