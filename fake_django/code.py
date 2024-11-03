from fake_django.model.model import BaseModel, DBModel
from fake_django.service.service import Service

class Doop(object):
    def doop(self) -> None:
        pass

def derp() -> None:
    pass

def get_base_model() -> BaseModel:
    return DBModel()

def get_db_model() -> DBModel:
    return DBModel()


def function() -> None:
    kwargs = {'a': 10, 'b': 12}

    model = DBModel()
    model.foo(10, 12)
    model.foo(**kwargs)

    model = get_base_model()
    model.foo(10, 12)
    model.foo(**kwargs)

    model = get_db_model()
    model.foo(10, 12)
    model.foo(**kwargs)

    svc = Service()
    svc.foo(10, 12)
    svc.foo(**kwargs)

    d = Doop()
    d.doop()
    derp()
