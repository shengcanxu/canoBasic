import unittest
from test.share import run_tokenize, run_interpreter, run_restore, run_save

# save nodes to file and load from file to restore the ast tree
filepath = "C:\\project\\canoBasic\\test\\archievetest.txt"
class Test_save(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_save('var a = "1ab"', filepath),
            "LN,1,VA,$a,@0"
        )
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("a"),
            "1ab"
        )

    def test_parse2(self):
        run_save('var a = 3 + 2 * 3 ^ 2', filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("a"),
            "21.0"
        )

    def test_parse4(self):
        run_save("var a = if 5 < 3 then 3 + 5 else 4 + 8", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("a"),
            "12"
        )

    def test_parse5(self):
        run_interpreter("var a = var b = 8")
        run_save("for i=6 to 1 step -2 then if b >= 6 then var b = b-2 else var b = b-1 ", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("b"),
            "3"
        )

    def test_parse6(self):
        run_interpreter("var a = var b = 8")
        run_save("while b >= 5 then if b >= 6 then var b = b-1 else var b = b-2 ", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("b"),
            "3"
        )

    def test_parse7(self):
        run_interpreter("fun test(a, b) -> a + b")
        run_interpreter("fun test2(a, b) -> a + b + test(a*2, b*3)")
        run_save("fun test3(a) -> a * test2(a, a + 1)", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("test3( test(1, 2) )"),
            "75"
        )

    def test_parse8(self):
        run_save('fun test(name, age) -> "hello, " * 3 + name + ", your age is: " + age', filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter('test("cano", "40")'),
            "hello, hello, hello, cano, your age is: 40"
        )

    def test_parse9(self):
        run_save("var a = [1, 2, 3, 4] \n\nis_list(3)\n\n", filepath)
        self.assertEqual(
            run_restore(filepath),
            "[[1,2,3,4],0]"
        )
        self.assertEqual(
            run_interpreter('a'),
            "[1,2,3,4]"
        )

    def test_parse10(self):
        run_save("var a = []\n\nfor i=0 to 10 then\n if i==4 then continue elif i==8 then break\n var a=a+i\n end", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter('a'),
            "[0,1,2,3,5,6,7]"
        )

    def test_parse10(self):
        run_save("var a = []\n\nvar i= 0\n\nwhile i<10 then\n var i=i+1\n if i==4 then continue elif i==8 then break\n var a=a+i\n end", filepath)
        run_restore(filepath)
        self.assertEqual(
            run_interpreter('a'),
            "[1,2,3,5,6,7]"
        )


if __name__ == '__main__':
    unittest.main()
