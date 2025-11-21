import threading

_local = threading.local()


def set_driver(driver):
    _local.driver = driver


def get_driver():
    return getattr(_local, 'driver', None)


def clear_driver():
    if hasattr(_local, 'driver'):
        try:
            _local.driver.quit()
        except Exception:
            pass
        del _local.driver
