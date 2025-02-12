import multiprocessing as mp
import os
import sys

dates = [
    "01042015",
    "02042015",
    "03042015",
    "04042015",
]
INTERVAL = sys.argv[1]


def consumer(date):
    interpreter = os.path.basename(sys.executable)
    os.system(f"{interpreter} main.py {date} {INTERVAL}")


def producer(dates, queue):
    for date in dates:
        orders_file = f"Orders/CASH_Orders_{date}.DAT.gz"
        trades_file = f"Trades/CASH_Trades_{date}.DAT.gz"
        if os.name == "nt":
            os.system(f".\\gzip_sort.exe {orders_file}")
            os.system(f".\\gzip_sort.exe {trades_file}")
        else:
            os.system(f"./gzip_sort {orders_file}")
            os.system(f"./gzip_sort {trades_file}")
        queue.put(date)


def worker(queue):
    while True:
        date = queue.get()
        if date is None:
            break
        consumer(date)


PREPROCESS_WORKERS = 1
MAIN_WORKERS = mp.cpu_count() - PREPROCESS_WORKERS - 1


def run():
    queue = mp.Queue()
    chunk_size = len(dates) // PREPROCESS_WORKERS + (
        len(dates) % PREPROCESS_WORKERS > 0
    )
    date_chunks = [dates[i : i + chunk_size] for i in range(0, len(dates), chunk_size)]

    preprocesses = [
        mp.Process(target=producer, args=(chunk, queue)) for chunk in date_chunks
    ]
    for p in preprocesses:
        p.start()

    main_processes = [
        mp.Process(target=worker, args=(queue,)) for _ in range(MAIN_WORKERS)
    ]
    for p in main_processes:
        p.start()

    for p in preprocesses:
        p.join()
    for _ in main_processes:
        queue.put(None)
    for p in main_processes:
        p.join()


if __name__ == "__main__":
    run()
