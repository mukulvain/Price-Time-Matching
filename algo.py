from Ticker import Ticker
from reader import order_repository, get_order, get_trade, get_symbols
import time


symbols = get_symbols()
tickers = {}
for symbol in symbols:
    tickers[symbol] = Ticker(symbol)


start = time.time()
order = get_order()
while True:
    trade = get_trade()
    if trade is None:
        break
    while order and order.order_time < trade.trade_time:
        stock = tickers[order.symbol]
        order_number = order.order_number
        if order_number in order_repository:
            previous_order = order_repository[order_number]
            if order.activity_type == "CANCEL":
                if order.is_buy:
                    stock.buy_book.delete(order_number, previous_order.is_stop_loss)
                else:
                    stock.sell_book.delete(order_number, previous_order.is_stop_loss)
                order = get_order()
                continue

            # Removes order
            elif order.activity_type == "MODIFY":
                if previous_order.is_buy:
                    stock.buy_book.delete(
                        order.order_number, previous_order.is_stop_loss
                    )
                else:
                    stock.sell_book.delete(
                        order.order_number, previous_order.is_stop_loss
                    )

        if not order.is_stop_loss and (order.is_market_order or order.is_ioc):
            order = get_order()
            continue

        # Adds order
        if order.is_buy:
            stock.buy_book.add(order)
        else:
            stock.sell_book.add(order)
        order_repository[order_number] = order
        order = get_order()

    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number
    stock = tickers[trade.symbol]
    stock.buy_book.delete(buyer, False, volume)
    stock.sell_book.delete(seller, False, volume)

end = time.time()
elapsed_time = end - start
print(f"Elapsed time: {elapsed_time:.6f} seconds")
