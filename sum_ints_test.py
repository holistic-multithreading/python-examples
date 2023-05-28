import unittest
import sum_ints

class TestSumInts(unittest.TestCase):

    def test_thread_counts(self):
        self.assertEqual(sum_ints.thread_counts(1), [])
        self.assertEqual(sum_ints.thread_counts(2), [2])
        self.assertEqual(sum_ints.thread_counts(4), [2, 4])
        self.assertEqual(sum_ints.thread_counts(10), [2, 4, 8, 10])
        self.assertEqual(sum_ints.thread_counts(12), [2, 4, 8, 12])
        self.assertEqual(sum_ints.thread_counts(15), [2, 4, 8, 15])
        self.assertEqual(sum_ints.thread_counts(16), [2, 4, 8, 16])

    def test_benchmark_name(self):
        self.assertEqual(sum_ints.benchmark_name('BaseName', 1_000), 'BaseName/1,000')
        self.assertEqual(sum_ints.benchmark_name('BaseName', 1_000, 10), 'BaseName/1,000/10')

    def test_single_thread_sum(self):
        self.assertEqual(sum_ints.singlethread_sum(1, 10), 45)
        self.assertEqual(sum_ints.singlethread_sum(1, 15), 60)
        self.assertEqual(sum_ints.singlethread_sum(1, 100), 450)

    def test_multithread_sum(self):
        self.assertEqual(sum_ints.multithread_sum(1, 10, 2), 45)
        self.assertEqual(sum_ints.multithread_sum(1, 15, 4), 60)
        self.assertEqual(sum_ints.multithread_sum(1, 100, 8), 450)
        self.assertEqual(sum_ints.multithread_sum(1, 100, 10), 450)

if __name__ == "__main__":
    unittest.main()
