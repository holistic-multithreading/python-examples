import asyncio
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import google_benchmark
from multiprocessing import cpu_count
from math import log2, exp2, ceil

def thread_counts(cpu_number=cpu_count()):
    return [ceil(exp2(i)) if exp2(i) <= cpu_number else cpu_number for i in range(1, ceil(log2(cpu_number)) + 1)]

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
    results = [[0] for _ in range(thread_count)]
    threads = [Thread(target=sum_values, args=[r[0], r[1], results[i]]) for i, r in enumerate(intervals(lo, hi, thread_count))]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return sum([r[0] for r in results])

def executor_sum(lo, hi, thread_count):
    sum = 0
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(singlethread_sum, r[0], r[1]) for r in intervals(lo, hi, thread_count)]
        for future in as_completed(futures):
            try:
                sum = sum + future.result()
            except Exception as ex:
                print('Exception computing sum of integers: %s' % ex)
    return sum

def process_pool_executor_sum(lo, hi, thread_count):
    sum = 0
    with ProcessPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(singlethread_sum, r[0], r[1]) for r in intervals(lo, hi, thread_count)]
        for future in as_completed(futures):
            try:
                sum = sum + future.result()
            except Exception as ex:
                print('Exception computing sum of integers: %s' % ex)
    return sum

def task_group_sum(lo, hi, thread_count):
    async def async_sum(lo, hi):
        return singlethread_sum(lo, hi)

    async def main():
        tasks = []
        async with asyncio.TaskGroup() as task_group:
            tasks = [task_group.create_task(async_sum(r[0], r[1])) for r in intervals(lo, hi, thread_count)]

        return sum([task.result() for task in tasks])

    return asyncio.run(main())

@google_benchmark.register
@google_benchmark.option.range_multiplier(1_000)
@google_benchmark.option.range(1_000, 1_000_000_000)
@google_benchmark.option.use_real_time()
def bm_single_thread_sum(state):
    while state:
       singlethread_sum(1, state.range(0)) 

@google_benchmark.register
@google_benchmark.option.args_product([[1_000, 1_000_000, 1_000_000_000], thread_counts()])
@google_benchmark.option.measure_process_cpu_time()
@google_benchmark.option.use_real_time()
def bm_multithreaded_sum(state):
    while state:
       multithread_sum(1, state.range(0), state.range(1)) 

@google_benchmark.register
@google_benchmark.option.args_product([[1_000, 1_000_000, 1_000_000_000], thread_counts()])
@google_benchmark.option.measure_process_cpu_time()
@google_benchmark.option.use_real_time()
def bm_thread_pool_executor_sum(state):
    while state:
       executor_sum(1, state.range(0), state.range(1)) 

@google_benchmark.register
@google_benchmark.option.args_product([[1_000, 1_000_000, 1_000_000_000], thread_counts()])
@google_benchmark.option.measure_process_cpu_time()
@google_benchmark.option.use_real_time()
def bm_process_pool_executor_sum(state):
    while state:
       process_pool_executor_sum(1, state.range(0), state.range(1)) 

@google_benchmark.register
@google_benchmark.option.args_product([[1_000, 1_000_000, 1_000_000_000], thread_counts()])
@google_benchmark.option.measure_process_cpu_time()
@google_benchmark.option.use_real_time()
def bm_task_group_sum(state):
    while state:
       task_group_sum(1, state.range(0), state.range(1)) 

if __name__ == "__main__":
    google_benchmark.main()
