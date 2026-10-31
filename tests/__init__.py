import sys
import os
import time
import unittest
from tests.CustomTestRunner import CustomTestRunner
from typing import List, Dict

def suiteToCaseList(testSuite : unittest.TestSuite) -> List[unittest.TestCase]:
    """Transforme la TestSuite and list de TestCase"""
    testCases = []
    for test in testSuite:
        if isinstance(test, unittest.TestSuite):
            testCases.extend(suiteToCaseList(test))
        else:
            testCases.append(test)
    return testCases

def printStart(resultats : Dict[type, unittest.TestResult], currentTestCase : type) -> None:
    resultats[currentTestCase]= unittest.TestCase().defaultTestResult()
    print("==========", currentTestCase.__name__,"==========")

def printFinish(resultats : Dict[type, unittest.TestResult], currentTestCase : type) -> None:
    successes= resultats[currentTestCase].testsRun - len(resultats[currentTestCase].errors) - len(resultats[currentTestCase].failures) - len(resultats[currentTestCase].unexpectedSuccesses)
    print("==========Reussis: ",successes,"/",resultats[currentTestCase].testsRun,"==========")


#on intercepte la recherche de tests, on cherche avec le bon pattern, on fait les runs manuellement puis on arrete tout
def load_tests(loader : unittest.TestLoader, standard_tests : unittest.TestSuite, pattern : str):
    testRunner= CustomTestRunner()
    testSuite= loader.discover(start_dir=os.path.basename(os.path.dirname(os.path.abspath(__file__))), pattern="Test*.py")
    testCases= suiteToCaseList(testSuite)
    if (len(testCases)==0):
        sys.exit(0)
    currentTestCase = type(testCases[0])
    resultats : Dict[type, unittest.TestResult]= {}
    printStart(resultats, currentTestCase)
    testTime= time.time()
    for test in testCases:
        if type(test) != currentTestCase:
            printFinish(resultats, currentTestCase)
            currentTestCase= type(test)
            printStart(resultats, currentTestCase)
        res= testRunner.run(test)
        resultats[currentTestCase].errors.extend(res.errors)
        resultats[currentTestCase].failures.extend(res.failures)
        resultats[currentTestCase].skipped.extend(res.skipped)
        resultats[currentTestCase].expectedFailures.extend(res.expectedFailures)
        resultats[currentTestCase].unexpectedSuccesses.extend(res.unexpectedSuccesses)
        resultats[currentTestCase].testsRun+= res.testsRun
        status= "Ok"
        if (len(res.errors)>0):
            status= "Error"
        if (len(res.failures)>0 or len(res.unexpectedSuccesses)>0):
            status= "Fail"
        print(test.id().split("test_")[1]+"... "+status)
    testTime= time.time() - testTime
    printFinish(resultats, currentTestCase)
    resultat= unittest.TestCase().defaultTestResult()
    for testCaseClass, res in resultats.items():
        resultat.errors.extend(res.errors)
        resultat.failures.extend(res.failures)
        resultat.skipped.extend(res.skipped)
        resultat.expectedFailures.extend(res.expectedFailures)
        resultat.unexpectedSuccesses.extend(res.unexpectedSuccesses)
        resultat.testsRun+= res.testsRun
    successes= resultat.testsRun - len(resultat.errors) - len(resultat.failures) - len(resultat.unexpectedSuccesses)
    fails= len(resultat.failures) + len(resultat.unexpectedSuccesses)
    errors= len(resultat.errors)
    print("Ran ",resultat.testsRun," tests in ", round(testTime, 3)," seconds")
    print("Successes: ", successes, " - Fails: ", fails, " - Errors: ", errors)
    output= unittest.TextTestResult(unittest.runner._WritelnDecorator(sys.stderr), False, 0)
    output.printErrorList("FAIL", resultat.failures)
    output.printErrorList("ERROR", resultat.errors)
    if resultat.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(0)