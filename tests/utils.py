# -*- coding: utf-8 -*-

class Spy(object):
    def __init__(self):
        self.args = []
        self.kwargs = []
        self.result = []
        self.call_count = 0

    def called_with(self, *args, **kwargs):
        assert self.args[0] == args
        assert self.kwargs[0] == kwargs

def spy_fn(target, fn_name):
    spy = Spy()
    fn = getattr(target, fn_name)

    def fn_wrap(*args, **kwargs):
        spy.args.append(args)
        spy.kwargs.append(kwargs)
        spy.result.append(fn(*args, **kwargs))
        spy.call_count += 1

    setattr(target, fn_name, fn_wrap)
    spy.restore = lambda: setattr(target, fn_name, fn)

    return spy
