from decorator import decorator
from paste import httpexceptions

@decorator
def authenticated_action(self, func, *args, **kwargs):
    if not request.environ.has_key('REMOTE_USER'):
        raise HTTPUnauthorized()
    return func(*args, **kwargs)
