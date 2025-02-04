import numpy as np
from sortedcontainers import SortedDict

from reader import order_repository


class Book:
    def __init__(self, buy=True):
        self.buy = buy
        self.queue = SortedDict()
        self.orders = {}
        self.stop_loss_orders = {}

    # Fetches the best price of the queue
    def fetch_price(self):
        if self.buy:
            return self.queue.peekitem()[0]
        else:
            return self.queue.peekitem(0)[0]

    def add(self, order):
        # Adds order to stop loss queue
        if order.is_stop_loss:
            if order.order_number in self.stop_loss_orders:
                del self.stop_loss_orders[order.order_number]
                order.is_stop_loss = False
                if order.is_market_order:
                    del order_repository[order.order_number]
                else:
                    order_repository[order.order_number].is_stop_loss = False
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
            del order_repository[order_number]

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

    def fetch_data(self, top):
        # Assumption: Client & Algo Category prices for non-top orders are not required.

        # Comment the following for details on all orders
        volumes_original = np.full((len(top), 2, 3), 0)
        volumes_disclosed = np.full((len(top), 2, 3), 0)

        # Uncomment the following for details on all orders
        # volumes_original = np.full((len(top), 2, 3), 0)
        # volumes_disclosed = np.full((len(top), 2, 3), 0)

        if self.buy:
            idx = 0
            prices = np.full((2, 3), 0)
            keys = list(self.queue.keys())
            keys.reverse()
            for key in keys:
                for order in self.queue[key]:
                    for i in range(len(top)):
                        if idx < top[i]:
                            volumes_original[i][order.algo][
                                order.client - 1
                            ] += order.volume_original
                            volumes_disclosed[i][order.algo][order.client - 1] += min(
                                order.volume_disclosed, order.volume_original
                            )
                    # Uncomment the following for details on all orders
                    # volumes_original[-1][order.algo][
                    #     order.client - 1
                    # ] += order.volume_original
                    # volumes_disclosed[-1][order.algo][order.client - 1] += min(
                    #     order.volume_disclosed, order.volume_original
                    # )
                    prices[order.algo][order.client - 1] = max(
                        order.limit_price, prices[order.algo][order.client - 1]
                    )
                idx += 1
                if idx >= top[-1]:
                    break
        else:
            idx = 0
            prices = np.full((2, 3), np.inf)
            for key in self.queue.keys():
                for order in self.queue[key]:
                    for i in range(len(top)):
                        if idx < top[i]:
                            volumes_original[i][order.algo][
                                order.client - 1
                            ] += order.volume_original
                            volumes_disclosed[i][order.algo][order.client - 1] += min(
                                order.volume_disclosed, order.volume_original
                            )
                    # Uncomment the following for details on all orders
                    # volumes_original[-1][order.algo][
                    #     order.client - 1
                    # ] += order.volume_original
                    # volumes_disclosed[-1][order.algo][order.client - 1] += min(
                    #     order.volume_disclosed, order.volume_original
                    # )
                    prices[order.algo][order.client - 1] = min(
                        order.limit_price, prices[order.algo][order.client - 1]
                    )
                idx += 1
                if idx >= top[-1]:
                    break
        return (
            np.concatenate((volumes_original.flatten(), volumes_disclosed.flatten())),
            prices.flatten(),
        )
