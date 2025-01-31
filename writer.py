import csv

import numpy as np


def write_line(stock):
    try:
        bid_volumes, bid_prices = stock.buy_book.fetch_data([1, 3, 5, 10])
        best_bid = stock.buy_book.fetch_price()
        ask_volumes, ask_prices = stock.sell_book.fetch_data([1, 3, 5, 10])
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
                [spread, stock.period],
            )
        )
        row = np.where(np.isinf(row), 0, row)
        row = row.astype(int)
        row = np.hstack((row, [stock.code]))

        with open("output.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)
    except:
        pass
