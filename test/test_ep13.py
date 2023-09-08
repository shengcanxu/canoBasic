import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP13(unittest.TestCase):
    def test_parse2(self):
        run_interpreter("fun test()\n var foo = 12\n return foo\n end")
        self.assertEqual(
            run_interpreter("test()"),
            "12"
        )

    def test_parse3(self):
        run_interpreter("fun test()\n var foo = 12\n return foo\n var foo = 15\n end")
        self.assertEqual(
            run_interpreter("test()"),
            "12"
        )

    def test_pars4(self):
        run_interpreter("var a = []")
        run_interpreter("for i=0 to 10 then\n if i==4 then continue elif i==8 then break\n var a=a+i\n end")
        self.assertEqual(
            run_interpreter("a"),
            "[0,1,2,3,5,6,7]"
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
