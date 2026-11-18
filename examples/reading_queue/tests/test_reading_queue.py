"""Behavioural regression tests for the reading queue."""

import unittest

from reading_queue import ReadingQueue


class ReadingQueueTests(unittest.TestCase):
    def setUp(self):
        self.queue = ReadingQueue()

    def test_empty_queue_starts_at_zero(self):
        self.assertEqual(self.queue.completed_count, 0)

    def test_completion_is_idempotent(self):
        self.queue.add("bk1", "The River")
        self.queue.complete("bk1")
        self.queue.complete("bk1")
        self.assertEqual(self.queue.completed_count, 1)
        self.assertTrue(self.queue.books["bk1"]["done"])

    def test_two_different_books(self):
        self.queue.add("bk1", "The River")
        self.queue.add("bk2", "The Bridge")
        self.queue.complete("bk1")
        self.queue.complete("bk2")
        self.assertEqual(self.queue.completed_count, 2)

    def test_uncompleted_book_does_not_affect_count(self):
        self.queue.add("bk1", "The River")
        self.assertEqual(self.queue.completed_count, 0)
        self.assertFalse(self.queue.books["bk1"]["done"])

    def test_missing_book_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.queue.complete("absent")

    def test_duplicate_book_id_is_rejected(self):
        self.queue.add("bk1", "The River")
        with self.assertRaises(ValueError):
            self.queue.add("bk1", "A Different Title")
        self.assertEqual(len(self.queue.books), 1)

    def test_completion_uses_correct_book(self):
        self.queue.add("bk1", "The River")
        self.queue.add("bk2", "The Bridge")
        self.queue.complete("bk2")
        self.assertFalse(self.queue.books["bk1"]["done"])
        self.assertTrue(self.queue.books["bk2"]["done"])
        self.assertEqual(self.queue.completed_count, 1)


if __name__ == "__main__":
    unittest.main()
