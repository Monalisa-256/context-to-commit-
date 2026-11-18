class ReadingQueue:
    """Keep a list of books and the number completed in this process."""

    def __init__(self):
        self.books: dict[str, dict[str, str | bool]] = {}
        self.completed_count = 0

    def add(self, book_id: str, title: str) -> None:
        if book_id in self.books:
            raise ValueError("book identifier already exists")
        self.books[book_id] = {"title": title, "done": False}

    def complete(self, book_id: str) -> None:
        book = self.books[book_id]
        if not book["done"]:
            book["done"] = True
            self.completed_count += 1
