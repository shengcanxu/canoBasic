import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP9(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize('"this is a test"'),
            "[TT_STRING:this is a test, TT_EOF]"
        )
        self.assertEqual(
            run_tokenize('"this is \t a test\n"'),
            "[TT_STRING:this is 	 a test\n, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser('var a = "this is a test"'),
            "(TT_IDENTIFIER:a, TT_EQ, TT_STRING:this is a test)"
        )

    def test_parse3(self):
        run_interpreter('var a = "this is a test, "')
        run_interpreter('var b = a + a')
        run_interpreter('var c = a * 3')
        self.assertEqual(
            run_interpreter("b"),
            "this is a test, this is a test, "
        )
        self.assertEqual(
            run_interpreter("c"),
            "this is a test, this is a test, this is a test, "
        )

    def test_pars4(self):
        run_interpreter('fun test(name, age) -> "hello, " * 3 + name + ", your age is: " + age')
        self.assertEqual(
            run_interpreter('test("cano", "40")'),
            "hello, hello, hello, cano, your age is: 40"
        )

if __name__ == '__main__':
    unittest.main()
