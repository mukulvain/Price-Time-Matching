import csv

import numpy as np

DATA_POINTS = [1, 5]


def write_header(filename):
    clients = ["C", "P", "R"]
    is_algo = ["A", "NA"]
    is_buy = ["Bid", "Ask"]
    volumes = ["Q"]
    header_list = []
    for buy in is_buy:
        for volume in volumes:
            for point in DATA_POINTS:
                for algo in is_algo:
                    for client in clients:
                        header_list.append(
                            client + algo + "_" + buy + "_" + str(point) + volume
                        )
        header_list.append("best_" + buy)
        for algo in is_algo:
            for client in clients:
                header_list.append(client + algo + "_best_" + buy)
    header_list.append("spread")
    header_list.append("period")
    header_list.append("date")
    header_list.append("symbol")
    with open(filename, mode="w", newline="") as file:
        csv.DictWriter(file, delimiter=",", fieldnames=header_list).writeheader()


def write_line(stock, period, date, filename):
    if bool(stock.buy_book.queue) and bool(stock.sell_book.queue):
        bid_volumes, bid_prices = stock.buy_book.fetch_data(DATA_POINTS)
        best_bid = stock.buy_book.fetch_price()
        ask_volumes, ask_prices = stock.sell_book.fetch_data(DATA_POINTS)
        best_ask = stock.sell_book.fetch_price()
        spread = best_ask - best_bid
        row = np.hstack(
            (
                bid_volumes,
                [best_bid],
                bid_prices,
                ask_volumes,
                [best_ask],
                ask_prices,
                [spread, period],
            )
        )
        row = np.where(np.isinf(row), 0, row)
        row = row.astype(int)
        row = np.hstack((row, [date, stock.code]))

        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)
    else:
        print(stock.code)
