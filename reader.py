import csv

from Order import Order
from Trade import Trade

order_repository = {}
symbols_file = "NSE500_2019.csv"


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


def line_reader(file_path):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


def get_symbols():
    symbols = []
    with open(symbols_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for line in file:
            symbols.append(line.strip())
    return symbols
