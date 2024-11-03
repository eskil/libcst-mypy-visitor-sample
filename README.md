# What

Trying out libcst-mypy with a libcst visitor. This demonstrates
writing linters that are type aware. Let's assume we want to write a
linter that disallows passing `**kwargs`` to subclasses of a
particular baseclass. For whatever reasons.

# How

## Metal/venv

The Makefile provides a few targets for setting up a venv and running the test;

```
make venv
source .venv/bin/activate
make deps
make test
```

## Devcontainer

* open folder with vscode and let it build the devcontainer
* open a terminal and run `python3 ./visit.py fake_django/code.py`

## Output

The output is
```
python3 ./visit.py fake_django/code.py
ERROR:__main__:Call at fake_django/code.py#L23:4, 'model.foo(**kwargs)' calls a BaseModel with **kwargs
ERROR:__main__:Call at fake_django/code.py#L27:4, 'model.foo(**kwargs)' calls a BaseModel with **kwargs
ERROR:__main__:Call at fake_django/code.py#L31:4, 'model.foo(**kwargs)' calls a BaseModel with **kwargs
```

In `fake_django`, there's a set of files/modules to fake a framework
with base models and services. Our goal is to be able to lint for
specific actions on subclasses of some of the frameworks' models.`

```
fake_django
├── __init__.py
├── bases
│   └── __init__.py # Defines `BaseModel` and `BaseService`
├── code.py         # The code that calls `DBModel` and `Service` we're linting
├── model
│   ├── __init__.py
│   └── model.py    # Defines `DBModel` as a subclass of `BaseModel`
└── service
    ├── __init__.py
    └── service.py  # Defines `Service` as a subclass of `BaseService`
```

* In `fake_django/bases` defines two MVC like base classes, `BaseModel`
  and `BaseService`.

* In `model` and `service`, define a subclass of each of the base classes.

* `code.py` is what we examine, it instantiates the subclasses and
  call functions on them. This is what we want to examine.

# Debug

Run the visitor with `-vv` for debug info

```
pyton3 ./visit.py -vv <file>
```

# Notes

* requirements lock to mypy-1.6.1, see [this bug](https://github.com/dosisod/refurb/issues/305) that
