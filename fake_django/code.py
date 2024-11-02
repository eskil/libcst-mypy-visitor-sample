from fake_django.model.model import DBModel
from fake_django.service.service import Service

class Doop(object):
    def doop(self) -> None:
        pass

def derp() -> None:
    pass

def function() -> None:
    model = DBModel()
    kwargs = {'a': 10, 'b': 12}
    model.foo(10, 12)
    model.foo(**kwargs)

    svc = Service()
    kwargs = {'a': 10, 'b': 12}
    svc.foo(10, 12)
    svc.foo(**kwargs)

    d = Doop()
    d.doop()
    derp()
