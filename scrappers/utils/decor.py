import time

def delayed_action(func):
    """to delay the execution of function by 5 seconds before and 2 seconds after

    Args:
        func (_type_): _description_
    """
    def wrapper(*args, **kwargs):
        time.sleep(5)
        r = func(*args, **kwargs)
        return r
    return wrapper
