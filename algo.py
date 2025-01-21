from Book import Book
from reader import order_repository, orders, trades

MARKET_OPENS_AT = 9.25


sell_book = Book(False)
buy_book = Book(True)
ineligible_orders = []
stack = []

idx = 0
for trade in trades:
    while orders[idx].order_time < trade.trade_time:
        order = orders[idx]
        order_number = order.order_number
        idx += 1

        if order_number in order_repository:
            if order.activity_type == "CANCEL":
                if order.is_buy:
                    buy_book.delete(order_number, order.is_stop_loss)
                else:
                    sell_book.delete(order_number, order.is_stop_loss)
                continue

            # Removes order
            elif order.activity_type == "MODIFY":
                previous_order = order_repository[order_number]
                if previous_order.is_buy:
                    buy_book.delete(order.order_number, previous_order.is_stop_loss)
                else:
                    sell_book.delete(order.order_number, previous_order.is_stop_loss)

        if not order.is_stop_loss and (order.is_market_order or order.is_ioc):
            continue

        # Adds order
        if order.is_buy:
            buy_book.add(order)
        else:
            sell_book.add(order)
        order_repository[order_number] = order

    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number

    buy_book.delete(buyer, False, volume)
    sell_book.delete(seller, False, volume)
