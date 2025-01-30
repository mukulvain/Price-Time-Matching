class Trade:
    def __init__(
        self,
        record,
        segment,
        trade_number,
        trade_time,
        symbol,
        series,
        trade_price,
        trade_quantity,
        buy_order_number,
        buy_algo,
        buy_client,
        sell_order_number,
        sell_algo,
        sell_client,
    ):
        self.record = record
        self.segment = segment
        self.trade_number = trade_number
        self.trade_time = trade_time
        self.symbol = symbol
        self.series = series
        self.trade_price = trade_price
        self.trade_quantity = trade_quantity
        self.buy_order_number = buy_order_number
        self.buy_algo = buy_algo % 2
        self.buy_client = buy_client
        self.sell_order_number = sell_order_number
        self.sell_algo = sell_algo % 2
        self.sell_client = sell_client
