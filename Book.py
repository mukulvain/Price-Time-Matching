from sortedcontainers import SortedDict
from reader import order_repository


class Book:
    def __init__(self, buy=True):
        self.buy = buy
        # Mathematical cosmetic
        self.buy_var = 2 * buy - 1

        self.queue = SortedDict()
        self.orders = {}
        self.stop_loss_orders = {}

    # Updates the best price of the queue
    def fetch_price(self):
        if self.buy:
            self.current_price = self.queue.peekitem()[0]
        else:
            self.current_price = self.queue.peekitem(0)[0]

    def add(self, order):
        # Adds order to stop loss queue
        if order.is_stop_loss:
            if order.order_number in self.stop_loss_orders:
                del self.stop_loss_orders[order.order_number]
                order.is_stop_loss = False
                if not order.is_market_order:
                    self.add(order)
            else:
                self.stop_loss_orders[order.order_number] = order
        # Adds order to the queue
        else:
            self.orders[order.order_number] = order.limit_price
            if order.limit_price not in self.queue:
                self.queue[order.limit_price] = [order]
            else:
                self.queue[order.limit_price].append(order)

    def delete(self, order_number, is_stop_loss, volume=0):
        if is_stop_loss:
            del self.stop_loss_orders[order_number]

        # Removes order from queue
        elif order_number in self.orders:
            price = self.orders[order_number]
            for i in range(len(self.queue[price])):
                if self.queue[price][i].order_number == order_number:
                    if not volume or self.queue[price][i].volume_original == volume:
                        self.queue[price].pop(i)
                        del self.orders[order_number]
                        del order_repository[order_number]
                    else:
                        self.queue[price][i].volume_original -= volume
                    break
            if not len(self.queue[price]):
                del self.queue[price]
