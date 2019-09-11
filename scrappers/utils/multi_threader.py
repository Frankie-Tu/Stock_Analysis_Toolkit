from concurrent.futures.thread import ThreadPoolExecutor


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
            if len(args) == 0:
                for thread in threads:
                    exe.submit(call_func, thread)
            else:
                for thread in threads:
                    exe.submit(call_func, thread, args)
