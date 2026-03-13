from astronverse.actionlib.atomic import atomicMg


class Hello:
    @staticmethod
    @atomicMg.atomic(
        "Hello",
        outputList=[atomicMg.param("greeting", types="Str")],
    )
    def say_hello(name: str = "World") -> str:
        return f"Hello, {name}!"
