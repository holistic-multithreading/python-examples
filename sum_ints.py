from threading import Thread
from pyperf import Runner

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

values = [1_000, 1_000_000, 1_000_000_000]
thread_counts = [2, 4, 8, 10, 12]
runner = Runner()

for tc in thread_counts:
    for v in values:
        runner.bench_func('/'.join(['MultithreadSum', f'{v:,}', str(tc)]), multithread_sum, 1, v, tc)

for v in values:
    runner.bench_func('/'.join(['SingleThreadSum', f'{v:,}']), singlethread_sum, 1, v)
