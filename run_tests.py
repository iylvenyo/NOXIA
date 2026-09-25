import sys
import unittest

# python .\run_tests.py
def run_tests():
    print("Running NOXIA backend tests...\n")

    loader = unittest.TestLoader()
    tests = loader.discover(
        start_dir="tests",
        pattern="test_*.py",
    )
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(tests)
    print()
    if results.wasSuccessful():
        print("All tests passed")
        return 0

    print("Some tests failed.")
    print("Failures:", len(results.failures))
    print("Errors:", len(results.errors))
    return 1

if __name__ == "__main__":
    sys.exit(run_tests())