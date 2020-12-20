import functools
import inspect


def result_as(classname):
    """ Client response decorator """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            def _parse(result):
                if hasattr(classname, 'from_dict'):
                    return classname.from_dict(data=result)
                return classname(**result)

            def _sync_response():
                """ Decorate synchronous request response """
                return _parse(result=fn_result)

            async def _async_response():
                """ Decorate asynchronous request response """
                _fn_result = await fn_result
                return _parse(result=_fn_result)

            # Execute function
            fn_result = function(*args, **kwargs)

            # Return decorated result depending on sync/async request
            if inspect.isawaitable(fn_result):
                return _async_response()
            return _sync_response()
        return wrapper
    return decorator
