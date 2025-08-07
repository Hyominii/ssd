import functools

def trace(logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cls_name = None
            actual_args = args

            # 클래스 메서드인 경우 클래스명 추출 & self 제외한 args 추출
            if args and hasattr(args[0], '__class__'):
                cls_name = args[0].__class__.__name__
                actual_args = args[1:]  # self 제외

            func_name = func.__name__

            location = f"{cls_name}.{func_name}()" if cls_name else f"{func_name}()"
            logger.print(location, f"호출됨 - args: {actual_args}, kwargs: {kwargs}")

            return func(*args, **kwargs)
        return wrapper
    return decorator
