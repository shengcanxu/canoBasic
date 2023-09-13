import unittest
from test.share import run_tokenize, run_interpreter, run_restore, run_save

# save nodes to file and load from file to restore the ast tree
filepath = "C:\\project\\canoBasic\\test\\archievetest.txt"
class TestEP13(unittest.TestCase):
    def test_parse2(self):
        self.assertEqual(
            run_save('var a = "1ab"', filepath),
            "LN,1,VA,$a,@0"
        )
        run_restore(filepath)
        self.assertEqual(
            run_interpreter("a"),
            "1ab"
        )


if __name__ == '__main__':
    unittest.main()
