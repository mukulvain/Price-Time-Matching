from Order import Order
from Trade import Trade


order_repository = {}


class AlphaNumeric:
    def __init__(self, length):
        self.value_type = str
        self.length = length


class Numeric:
    def __init__(self, length):
        self.value_type = int
        self.length = length


order = [
    AlphaNumeric(2),
    AlphaNumeric(4),
    Numeric(16),
    Numeric(14),
    AlphaNumeric(1),
    Numeric(1),
    AlphaNumeric(10),
    AlphaNumeric(2),
    Numeric(8),
    Numeric(8),
    Numeric(8),
    Numeric(8),
    AlphaNumeric(1),
    AlphaNumeric(1),
    AlphaNumeric(1),
    AlphaNumeric(1),
    AlphaNumeric(1),
]

trade = [
    AlphaNumeric(2),
    AlphaNumeric(4),
    Numeric(16),
    Numeric(14),
    AlphaNumeric(10),
    AlphaNumeric(2),
    Numeric(8),
    Numeric(8),
    Numeric(16),
    Numeric(1),
    Numeric(1),
    Numeric(16),
    Numeric(1),
    Numeric(1),
]


def to_order(line):
    ptr = 0
    order_args = []
    for var in order:
        order_args.append(var.value_type(line[ptr : ptr + var.length]))
        ptr += var.length
    return Order(*order_args)


def to_trade(line):
    ptr = 0
    trade_args = []
    for var in trade:
        trade_args.append(var.value_type(line[ptr : ptr + var.length]))
        ptr += var.length
    return Trade(*trade_args)


orders_file = "CASH_Orders_20082019.DAT"
trades_file = "CASH_Trades_20082019.DAT"


def line_reader(file_path):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


order_reader = line_reader(orders_file)
trade_reader = line_reader(trades_file)


def get_trade():
    try:
        return to_trade(next(trade_reader))
    except StopIteration:
        return None


def get_order():
    try:
        return to_order(next(order_reader))
    except StopIteration:
        return None

def get_symbols():
    symbols = []
    with open("symbols.txt", "r", encoding="utf-16") as file:
        for line in file:
            symbols.append(line.strip())
    return symbols
