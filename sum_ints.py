from threading import Thread
import google_benchmark
from multiprocessing import cpu_count
from math import log2, exp2, ceil

def thread_counts(cpu_number=cpu_count()):
    return [ceil(exp2(i)) if exp2(i) <= cpu_number else cpu_number for i in range(1, ceil(log2(cpu_number)) + 1)]

def benchmark_name(base_name, value, thread_count=None):
    return '/'.join(filter(None, [base_name, f'{value:,}', str(thread_count or '')]))

def intervals(lo, hi, thread_count):
    batch_size = (hi - lo + 1) // thread_count
    return [(lo + i*batch_size, lo + (i+1) * batch_size - 1 if i < thread_count - 1 else hi) for i in range(thread_count)]

def sum_values(lo, hi, result):
    result[0] = sum(i % 10 for i in range(lo, hi + 1))

def singlethread_sum(lo, hi):
    result = [0]
    sum_values(lo, hi, result)
    return result[0]

def multithread_sum(lo, hi, thread_count):
    results = [[0] for i in range(thread_count)]
    threads = [Thread(target=sum_values, args=[r[0], r[1], results[i]]) for i, r in enumerate(intervals(lo, hi, thread_count))]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return sum([r[0] for r in results])

@google_benchmark.register
@google_benchmark.option.range_multiplier(1_000)
@google_benchmark.option.range(1_000, 1_000_000_000)
@google_benchmark.option.use_real_time()
@google_benchmark.option.unit(google_benchmark.kMillisecond)
def bm_single_thread_sum(state):
    while state:
       singlethread_sum(1, state.range(0)) 

@google_benchmark.register
@google_benchmark.option.args_product([[1_000, 1_000_000, 1_000_000_000], thread_counts()])
@google_benchmark.option.measure_process_cpu_time()
@google_benchmark.option.use_real_time()
@google_benchmark.option.unit(google_benchmark.kMillisecond)
def bm_multithreaded_sum(state):
    while state:
       multithread_sum(1, state.range(0), state.range(1)) 

if __name__ == "__main__":
    google_benchmark.main()
