from threading import Thread
from pyperf import Runner
from multiprocessing import cpu_count
from math import log2, exp2, ceil

def thread_counts(cpu_number=cpu_count()):
    return [ceil(exp2(i)) if exp2(i) <= cpu_number else cpu_number for i in range(1, ceil(log2(cpu_number)) + 1)]

def benchmark_name(base_name, value, thread_count=None):
    return '/'.join(filter(None, [base_name, f'{value:,}', str(thread_count or '')]))

def sum_values(lo, hi, result):
    for i in range(lo, hi + 1):
        result[0] += i % 10

def singlethread_sum(lo, hi):
    result = [0]
    sum_values(lo, hi, result)
    return result[0]

def multithread_sum(lo, hi, thread_count):
    batch_size = (hi - lo + 1) // thread_count
    threads = []
    results = []
    start = lo
    for i in range(thread_count):
        end = start + batch_size - 1 if i < thread_count - 1 else hi
        results.append([0])
        threads.append(Thread(target=sum_values, args=[start, end, results[i]]))
        threads[i].start()
        start = end + 1

    sum = 0
    for i, thread in enumerate(threads):
        thread.join()
        sum += results[i][0]
    return sum

if __name__ == "__main__":
    values = [1_000, 1_000_000, 1_000_000_000]
    runner = Runner()

    for v in values:
        runner.bench_func(benchmark_name('SingleThreadSum', v), singlethread_sum, 1, v)

    for tc in thread_counts():
        for v in values:
            runner.bench_func(benchmark_name('MultithreadSum', v, tc), multithread_sum, 1, v, tc)
