from tenacity import wait_exponential, wait_fixed, wait_random_exponential


def fixed(seconds: float = 1.0):
    return wait_fixed(seconds)


def exponential(multiplier: float = 1.0, min_wait: float = 1.0, max_wait: float = 10.0):
    return wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait)


def exponential_jitter(min_wait: float = 1.0, max_wait: float = 10.0):
    return wait_random_exponential(min=min_wait, max=max_wait)