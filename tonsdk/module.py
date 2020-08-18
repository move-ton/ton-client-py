import ctypes

from tonsdk.mixins import TonRequestMixin


class TonModule(TonRequestMixin):
    """
    Base TON Module class.
    All modules, such as 'crypto', 'contracts', etc. should be inherited
    from this class.
    """
    def __init__(self, ctx: ctypes.c_int32):
        self._ctx = ctx
