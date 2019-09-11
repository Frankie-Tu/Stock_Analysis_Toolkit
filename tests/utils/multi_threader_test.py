import unittest
import time

from scrappers.utils.multi_threader import MultiThreader


def test_func_varg(name, *arg):
    print("thread {} start...".format(name))
    time.sleep(2)
    print("thread {}, optional arg: {}".format(name, arg))
    print("thread {} finished...".format(name))


def test_func(name):
    print("thread {} start...".format(name))
    time.sleep(2)
    print("thread {} finished...".format(name))


class MultiThreaderTest(unittest.TestCase):
    def test(self):
        processes = ["p1","p2","p3","p4","p5"]
        MultiThreader.run_thread_pool(processes, test_func_varg, 2, "optional_arg1", "optional_arg2")
        MultiThreader.run_thread_pool(processes, test_func, 2)
