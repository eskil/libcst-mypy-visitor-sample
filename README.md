# What
Trying out libcst-mypy with a libcst visitor. This demonstrates how we
can write linters that are type aware.

# How

The Makefile is just to provide some quick help with env/running
```
make venv
source .venv/bin/activate
make deps
make test
```

In `fake_django`, there's a set of files/modules to fake a framework
with base models and services. Our goal is to be able to lint for
specific actions on subclasses of some of the frameworks' models.`

Run the visitor with `-vv` for debug info
```
pyton3 ./visit.py -vv <file>
```

Output is ala

```
$ python3 ./visit.py fake_django/code.py  -v
INFO:__main__:args: Namespace(verbose=1, paths=[['fake_django/code.py']])
WARNING:__main__:Call at fake_django/code.py#L12:12, 'DBModel()' has no type signature
WARNING:__main__:Call at fake_django/code.py#L16:4, 'model.foo(a b)' calls a 'fake_django.model.model.DBModel' which inherits from ['fake_django.bases.BaseModel'] with arguments ['a', 'b']
WARNING:__main__:Call at fake_django/code.py#L17:4, 'model.foo(**kwargs)' calls a 'fake_django.model.model.DBModel' which inherits from ['fake_django.bases.BaseModel'] with arguments ['**kwargs']
ERROR:__main__:Call at fake_django/code.py#L17:4, 'model.foo(**kwargs)' calls a BaseModel with **kwargs
WARNING:__main__:Call at fake_django/code.py#L19:10, 'Service()' has no type signature
WARNING:__main__:Call at fake_django/code.py#L21:4, 'svc.foo(10 12)' calls a 'fake_django.service.service.Service' which inherits from ['fake_django.bases.BaseService'] with arguments ['10', '12']
WARNING:__main__:Call at fake_django/code.py#L22:4, 'svc.foo(**kwargs)' calls a 'fake_django.service.service.Service' which inherits from ['fake_django.bases.BaseService'] with arguments ['**kwargs']
WARNING:__main__:Call at fake_django/code.py#L24:8, 'Doop()' has no type signature
WARNING:__main__:Call at fake_django/code.py#L25:4, 'd.doop()' calls a 'fake_django.code.Doop' which inherits from ['builtins.object'] with arguments []
WARNING:__main__:Call at fake_django/code.py#L26:4, 'derp()' has no type signature
```

# Notes

* lock to mypy-1.6.1, see https://github.com/dosisod/refurb/issues/305
