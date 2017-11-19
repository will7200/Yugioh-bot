import time


def loop_scan(fn, **kwargs):
    limit = 3
    doit = True
    l_times = 0
    while doit and l_times <= limit:
        l_times += 1
        doit = fn(**kwargs)
        time.sleep(1)

