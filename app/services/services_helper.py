from functools import wraps

def with_uow(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        async with self.uow:
            return await f(self, *args, **kwargs)
    return wrapper