from fake_django.model.model import DBModel
from fake_django.service.service import Service

class Doop(object):
    def doop(self) -> None:
        pass

def derp() -> None:
    pass

model = DBModel()
kwargs = {'a': 10, 'b': 12}
model.foo(**kwargs)

svc = Service()
kwargs = {'a': 10, 'b': 12}
svc.foo(**kwargs)

d = Doop()
d.doop()
derp()
