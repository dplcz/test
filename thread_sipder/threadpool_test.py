# 线程池
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
import time


def sleep_task(sleep_time):
    print('sleep {}s'.format(sleep_time))
    time.sleep(sleep_time)
    print('end')


# max_workers工作线程
excutor = ThreadPoolExecutor(max_workers=2)
# 直接传参，不需要使用元组类型
task_1 = excutor.submit(sleep_task, 2)
task_2 = excutor.submit(sleep_task, 3)
task_3 = excutor.submit(sleep_task, 4)
# # 判断线程是否完成
# time.sleep(2.1)
# print(task_1.done())
# 取消还为进行的线程

# cancel_status = task_1.cancel()
# print(cancel_status)
# print(task_2.cancel())
# print(task_3.cancel())

# # 使用wait()方法等待线程结束  ALL_COMPLETED所有线程结束
# wait([task_1, task_2, task_3], return_when=ALL_COMPLETED)
# print('main end')

# 使用as_completed()方法判断单个线程的执行情况     还可以拿到线程的返回值
all_task = [task_1, task_2, task_3]
for task in as_completed(all_task):
    print(task)
