class ReadingQueue:
    def __init__(self):
        self.books = {}
        self.completed_count = 0

    def add(self, book_id: str, title: str):
        if book_id in self.books:
            raise ValueError("book identifier already exists")
        self.books[book_id] = {"title": title, "done": False}

    def complete(self, book_id: str):
        book = self.books[book_id]
        book["done"] = True
        self.completed_count += 1  # This is the defect the exercise reproduces.
