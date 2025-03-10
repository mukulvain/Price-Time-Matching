import csv


def write_header(filename):
    header_list = ["date", "trade_number", "time", "symbol", "Bid", "Ask", "spread"]
    with open(filename, mode="w", newline="") as file:
        csv.DictWriter(file, delimiter=",", fieldnames=header_list).writeheader()


def write_line(stock, date, trade_number, time, filename):
    if bool(stock.buy_book.queue) and bool(stock.sell_book.queue):
        spread = stock.previous_ask - stock.previous_bid
        later_spread = stock.sell_book.fetch_price() - stock.buy_book.fetch_price()
        row = [
            date,
            trade_number,
            time,
            stock.code,
            stock.previous_bid,
            stock.previous_ask,
            spread,
        ]
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)
