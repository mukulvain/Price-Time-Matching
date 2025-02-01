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
output_file = sys.argv[3]
INTERVAL = int(sys.argv[4])
order_reader = line_reader(orders_file)
trade_reader = line_reader(trades_file)

MARKET_OPENS = time(9, 15, 0)

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
trade = None
while True:
    previous_trade = trade
    trade = get_trade(trade_reader)
    if trade is None:
        for ticker in tickers.keys():
            write_line(tickers[ticker], output_file)
        break
    if previous_trade and trade.trade_time < previous_trade.trade_time:
        while order.order_time > previous_order.order_time:
            previous_order = order
            order = get_order(order_reader)
    if trade.symbol not in symbols:
        continue

    converted_time = clock_time(trade.trade_time)
    stock = tickers[trade.symbol]
    while converted_time > stock.threshold:
        write_line(stock, output_file)
        stock.period += 1
        stock.threshold = add_time(stock.threshold, INTERVAL)

    while order and order.order_time < trade.trade_time:
        previous_order = order
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
