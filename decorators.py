import functools

def log(func):
    """Dekorátor pro logování vstupních parametrů a výstupní hodnoty funkce."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f">Volání: {func.__name__} s args={args} a kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f">{func.__name__} vrací: {result}")
        return result

def log_decorator(func):
    """Dekorátor pro logování vstupních parametrů a výstupní hodnoty funkce."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Volání: {func.__name__} s args={args} a kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"{func.__name__} vrací: {result}")
            return result
        except Exception as e:
            print(f"Chyba ve funkci {func.__name__}: {e}")
            raise  # Přepošleme chybu dál
    return wrapper