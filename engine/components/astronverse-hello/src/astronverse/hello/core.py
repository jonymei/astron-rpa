from abc import ABC, abstractmethod


class IHelloCore(ABC):
    @staticmethod
    @abstractmethod
    def print(msg: str = "") -> str:
        pass


class HelloCore(IHelloCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "win {}".format(msg)
