import time
import multiprocessing
import random


class Test:
    def __init__(self, a, test2):
        self.a = a
        self.test2 = test2

    def test(self, ch, ch2):
        time.sleep(ch)
        print(ch)
        self.test2.some = random.randint(1, 100)
        self.test2.get()


class Test2:
    def __init__(self):
        self.some = 4

    def get(self):
        print(self.some)


def start_recover(test2):
    processes = list()
    for i in range(3):
        test = Test(3, test2)
        pr = multiprocessing.Process(target=test.test, args=(1, 3))
        processes.append(pr)
        pr.start()
    for pr in processes:
        pr.join()


if __name__ == "__main__":
    test2 = Test2()
    start_recover(test2)
