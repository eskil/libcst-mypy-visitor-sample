from fake_django.bases import BaseModel

class DBModel(BaseModel):
    def foo(self, a: int, b: int) -> None:
        print(f"DBModel::foo({a}, {b})")
