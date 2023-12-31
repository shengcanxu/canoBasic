import unittest
from test.share import run_tokenize, run_interpreter, run_parser

class TestEP13(unittest.TestCase):
    def test_parse2(self):
        self.assertEqual(
            run_tokenize("# hello\n## asdf##\n1+2"),
            "[1, PLS, 2, EOF]"
        )

    def test_parse3(self):
        self.assertEqual(
            run_interpreter("len([1,2,3,4])"),
            "4"
        )

    def test_pars4(self):
        self.assertEqual(
            run_interpreter('run("C:/project/canoBasic/test/example.test")'),
            "[<function test>,4]"
        )

    def test_pars5(self):
        run_interpreter("var a = []")
        run_interpreter("var i= 0")
        run_interpreter("while i<10 then\n var i=i+1\n if i==4 then continue elif i==8 then break\n var a=a+i\n end")
        self.assertEqual(
            run_interpreter("a"),
            "[1,2,3,5,6,7]"
        )

if __name__ == '__main__':
    unittest.main()
