from Book import Book
from reader import symbols

class Ticker:
    def __init__(self, code):
        self.code = code
        self.buy_book = Book(True)
        self.sell_book = Book(False)

tickers = {}
for symbol in symbols:
    tickers[symbol] = Ticker(symbol)