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
from writer import write_header, write_line

date = sys.argv[1]
INTERVAL = int(sys.argv[2])
orders_file = f"Orders/CASH_Orders_{date}.DAT.gz"
trades_file = f"Trades/CASH_Trades_{date}.DAT.gz"
output_file = f"LOB/LOB_{date}.csv"

write_header(output_file)
order_reader = line_reader(orders_file)
trade_reader = line_reader(trades_file)

MARKET_OPENS = time(9, 15, 0)

symbols = get_symbols()
tickers = {}
for symbol in symbols:
    tickers[symbol] = Ticker(symbol)


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
threshold = MARKET_OPENS
period = 0
stocks = set()
while True:
    previous_trade = trade
    trade = get_trade(trade_reader)
    if trade is None:
        for _ in stocks:
            write_line(tickers[_], date, output_file, period)
        break
    if previous_trade and trade.trade_time < previous_trade.trade_time:
        stocks = set()
        period = 0
        threshold = MARKET_OPENS
        while order.order_time > previous_order.order_time:
            previous_order = order
            order = get_order(order_reader)
    if trade.symbol not in symbols:
        continue
    stocks.add(trade.symbol)
    converted_time = clock_time(trade.trade_time)
    stock = tickers[trade.symbol]

    while order and order.order_time < trade.trade_time:
        min_time = min(converted_time, threshold)
        while order and clock_time(order.order_time) < min_time:
            previous_order = order
            if (
                order.symbol not in symbols
                or order.series != "EQ"
                or order.segment != "CASH"
            ):
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

        if min_time != converted_time:
            for _ in stocks:
                write_line(tickers[_], date, output_file, period)
            period += 1
            threshold = add_time(threshold, INTERVAL)

    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number
    stock.buy_book.delete(buyer, False, volume)
    stock.sell_book.delete(seller, False, volume)

end = tm.time()
elapsed_time = end - start
print(f"Elapsed time: {elapsed_time:.6f} seconds")
