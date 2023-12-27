import time


def retry(func):
    def wrapper(*args, **kwargs):
        retry_count = 30
        while retry_count != 0:
            try:
                r = func(*args, **kwargs)
                return r
            except:
                pass
            retry_count -= 1
            time.sleep(2)
        
        raise Exception(f"function {func} has exceeded number of retries...")
            
    return wrapper