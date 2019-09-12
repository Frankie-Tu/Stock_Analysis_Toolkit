from concurrent.futures.thread import ThreadPoolExecutor

import traceback


class MultiThreader:
    @staticmethod
    def run_thread_pool(threads, call_func, max_threads, *args):
        """
        :param threads: list of thread to be run concurrently
        :param call_func: calling function(thread, *args)
        :param max_threads: max concurrency
        :return: None
        """
        with ThreadPoolExecutor(max_workers=max_threads) as exe:
            futures = [exe.submit(call_func, thread, *args) for thread in threads]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    traceback.print_tb(e.__traceback__)
