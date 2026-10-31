import unittest

class CustomTestRunner(unittest.TextTestRunner):
    def run(self, test):
        if type(test)==unittest.TestSuite:
            return super().run(test)
        else:
            return test.run(result=unittest.TestResult())