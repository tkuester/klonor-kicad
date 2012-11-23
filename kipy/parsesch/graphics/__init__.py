'''
The only thing this package exports is parsesheet.

However, internally, a few modules need to "wire themselves in."

That is what _init() accomplishes.
'''

def _init():
    from ..graphics import primitives, components, labels
_init()
del _init

from .parse import parsesheet
