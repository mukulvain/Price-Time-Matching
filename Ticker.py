from Book import Book


class Ticker:
    def __init__(self, code):
        self.code = code
        self.buy_book = Book(True)
        self.sell_book = Book(False)
