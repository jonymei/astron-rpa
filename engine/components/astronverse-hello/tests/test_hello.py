import unittest

from astronverse.hello.hello import Hello


class TestHello(unittest.TestCase):
    def test_say_hello_returns_greeting(self):
        result = Hello.say_hello(name="Astron")
        self.assertEqual(result, "Hello, Astron!")

    def test_say_hello_uses_default_name(self):
        result = Hello.say_hello()
        self.assertEqual(result, "Hello, World!")
