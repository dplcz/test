import queue
from queue import Queue

if __name__ == '__main__':
    message_queue = Queue(maxsize=2)

    message_queue.put('dplcz666')
    message_queue.put('dplcz')
    # print('put dplcz')
    # # put方法是阻塞的，添加timeout属性，并使用异常处理可以设置等待时间
    # # message_queue.put('dp', timeout=3)
    # try:
    #     message_queue.put('dp', timeout=3)
    #     # 使用put_nowait()方法，如果不能插入数据则直接抛出异常
    #     message_queue.put_nowait('dp666')
    # except queue.Full as e:
    #     pass
    # print('end')
    message = message_queue.get()
    print(message)
    message = message_queue.get()
    print(message)
