import sys
import time as tm
from datetime import time

from reader import (
    add_time,
    clock_time,
    get_order,
    get_symbols,
    get_trade,
    line_reader,
    order_repository,
)
from Ticker import Ticker
from writer import write_line

orders_file = sys.argv[1]
trades_file = sys.argv[2]
order_reader = line_reader(orders_file)
trade_reader = line_reader(trades_file)

MARKET_OPENS = time(9, 15, 0)
INTERVAL = 300

symbols = get_symbols()
tickers = {}
for symbol in symbols:
    tickers[symbol] = Ticker(symbol, add_time(MARKET_OPENS, INTERVAL), 1)


def add_order(stock, order):
    if order.is_buy:
        stock.buy_book.add(order)
    else:
        stock.sell_book.add(order)


def delete_order(stock, order):
    if order.is_buy:
        stock.buy_book.delete(order.order_number, order.is_stop_loss)
    else:
        stock.sell_book.delete(order.order_number, order.is_stop_loss)


start = tm.time()
order = get_order(order_reader)
while True:
    trade = get_trade(trade_reader)
    if trade is None:
        for stock in tickers:
            write_line(stock)
        break

    if trade.symbol not in symbols:
        continue

    converted_time = clock_time(trade.trade_time)
    stock = tickers[trade.symbol]
    if converted_time > stock.threshold:
        write_line(stock)
        stock.period += 1
        stock.threshold = add_time(stock.threshold, INTERVAL)

    while order and order.order_time < trade.trade_time:
        if order.symbol not in symbols:
            order = get_order(order_reader)
            continue
        stock = tickers[order.symbol]
        order_number = order.order_number
        if order_number in order_repository:
            previous_order = order_repository[order_number]

            if order.activity_type == "CANCEL":
                delete_order(stock, previous_order)
                order = get_order(order_reader)
                continue

            elif order.activity_type == "MODIFY":
                delete_order(stock, previous_order)

        if not order.is_stop_loss and (order.is_market_order or order.is_ioc):
            order = get_order(order_reader)
            continue

        # Adds order
        add_order(stock, order)
        order_repository[order_number] = order
        order = get_order(order_reader)

    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number
    stock = tickers[trade.symbol]
    stock.buy_book.delete(buyer, False, volume)
    stock.sell_book.delete(seller, False, volume)

end = tm.time()
elapsed_time = end - start
print(f"Elapsed time: {elapsed_time:.6f} seconds")
