from fake_django.bases import BaseService

class Service(BaseService):
    def foo(self, a: int, b: int) -> None:
        print(f"Service::foo({a}, {b})")
