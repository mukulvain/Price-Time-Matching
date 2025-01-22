from Ticker import tickers
from reader import order_repository, orders, trades


idx = 0
for trade in trades:
    while orders[idx].order_time < trade.trade_time:
        order = orders[idx]
        stock = tickers[order.symbol]
        order_number = order.order_number
        idx += 1

        if order_number in order_repository:
            if order.activity_type == "CANCEL":
                if order.is_buy:
                    stock.buy_book.delete(order_number, order.is_stop_loss)
                else:
                    stock.sell_book.delete(order_number, order.is_stop_loss)
                continue

            # Removes order
            elif order.activity_type == "MODIFY":
                previous_order = order_repository[order_number]
                if previous_order.is_buy:
                    stock.buy_book.delete(
                        order.order_number, previous_order.is_stop_loss
                    )
                else:
                    stock.sell_book.delete(
                        order.order_number, previous_order.is_stop_loss
                    )

        if not order.is_stop_loss and (order.is_market_order or order.is_ioc):
            continue

        # Adds order
        if order.is_buy:
            stock.buy_book.add(order)
        else:
            stock.sell_book.add(order)
        order_repository[order_number] = order

    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number
    stock = tickers[trade.symbol]
    stock.buy_book.delete(buyer, False, volume)
    stock.sell_book.delete(seller, False, volume)