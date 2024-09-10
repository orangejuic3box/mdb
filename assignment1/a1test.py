# CMPUT 455 assignment 1 testing script
# Run using: python3 a1test.py aX.py assignmentX-public-tests.txt [-v]
# Where X is the current assignment number

import subprocess
import sys
import time
import signal
import os
import re

# Default maximum command execution time in seconds
DEFAULT_TIMEOUT = 1

# Color codes
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"

# Functions necessary for checking timeouts
class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException("Function timed out.")

# Class for specifying tests and recording results
class Test:
    def __init__(self, command, expected, id):
        self.command = command
        self.expected = expected
        self.id = id
        self.received = ""
        self.passed = None
        self.matched = None
        self.notes = ""

    # Printed representation of a test
    def __str__(self):
        s = " === Test "+ str(self.id) +" === \nCommand: '" + self.command + "'\nExpected: "
        
        if "\n" in self.expected[:-1]:
            s += "\n'\n" + self.expected + "'\n"
        else:
            s += "'" + self.expected.strip() + "'\n"

        s += "Received: "
        if "\n" in self.received.strip():
            s += "\n'\n"
        else:
            s += "'"

        if self.matched:
            s += f"{GREEN}" + self.received
        else:
            matching = True
            s += f"{GREEN}"
            for i in range(len(self.received.strip())):
                if i < len(self.expected) and self.expected[i] == self.received[i]:
                    if not matching:
                        s += f"{RESET}" + f"{GREEN}"
                else:
                    if matching:
                        s += f"{RESET}" + f"{RED}"
                s += self.received[i]

        if "\n" not in self.received.strip():
            s = s.strip()
        s += f"{RESET}'\n"

        if self.passed and self.matched:
            s += f"{GREEN}+ Success{RESET}\n"
        
        if not self.passed:
            s += f"{RED}- This command failed with error:\n'" + self.notes + f"'{RESET}\n"

        return s.strip()+"\n"
    
# Convert a test file into test objects
def file_to_tests(file_name):
    test_lines = []
    with open(file_name, "r") as tf:
        test_lines = tf.readlines()

    i = 0
    while i < len(test_lines):
        # Strip comments
        test_lines[i] = test_lines[i].split("#")[0].strip()
        # Delete whitespace lines
        if len(test_lines[i]) == 0:
            del test_lines[i]
        else:
            i += 1

    # Create tests
    tests = []
    i = 0
    while i < len(test_lines):
        command = test_lines[i]
        i += 1
        expected = test_lines[i] + "\n"
        while test_lines[i][0] != '=':
            i += 1
            expected += test_lines[i] + "\n"
        tests.append(Test(command, expected, len(tests)+1))
        i += 1
    return tests

# Send a command, returns whether the command passed, the output received, and any error messages
def send_command(process, command, expected_fail = False, timeout = DEFAULT_TIMEOUT):
    try:
        process.stdin.write(command+"\n")
        process.stdin.flush()
        output = ""
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            line = process.stdout.readline()
            while line[0] != "=":
                if len(line.strip()) > 0:
                    output += line
                line = process.stdout.readline()
            signal.alarm(0)
            output += line
            process.stdout.flush()

            if '= -1' in line and not expected_fail:
                return False, output, "Command failed with return code -1."
            else:
                return True, output, ""
        
        except TimeoutException:
            return False, output, "Command timeout, exceeded maximum allowed time of " + str(timeout) + " seconds."

    except Exception as e:
        return False, "", "Process error:\n" + str(e)

def perform_test(process, test):
    test.passed, test.received, test.notes = send_command(process, test.command, expected_fail="= -1" in test.expected)
    if test.expected[0] == '@':
        exp_pattern = re.compile((test.expected.strip())[1:], re.DOTALL)
        test.matched = exp_pattern.match(test.received.strip())
    else:
        test.matched = test.expected == test.received
    return test.matched

# Test a given process on a number of tests. Prints and returns results.
def test_process(process, tests, verbose=False, print_output=False):
    t0 = time.time()
    successful = []
    failed = []
    mismatched = []
    test_num = 1
    for test in tests:
        if print_output:
            print("Test", test_num, "/", len(tests), "(" + str(round(100 * test_num / len(tests))) + "%)", end="\r")
        test_num += 1
        perform_test(process, test)
        if not test.passed:
            failed.append(test)
        elif not test.matched:
            mismatched.append(test)
        else:
            successful.append(test)        

    if print_output:
        print()
        if verbose:
            for test in tests:
                print(test)

        print(f"{BLUE}\tFailed commands (" + str(len(failed)) + f"):\n{RESET}")
        for test in failed:
            print(test)
        print(f"{BLUE}\tSuccessful commands with mismatched outputs: (" + str(len(mismatched)) + f"):\n{RESET}")
        for test in mismatched:
            print(test)
        print(f"{BLUE}\tSummary report:\n{RESET}")
        print(len(tests), "Tests performed")
        print(f"{GREEN}" + str(len(successful)) + " Successful (" + str(round(100*len(successful) / len(tests))) + f"%){RESET}")
        print(f"{RED}" + str(len(failed)) + " Failed (" + str(round(100*len(failed) / len(tests))) + f"%){RESET}")
        print(f"{RED}" + str(len(mismatched)) + " Mismatched (" + str(round(100*len(mismatched) / len(tests))) + f"%){RESET}")
        print("\nFinished in", round(time.time() - t0, 2), "seconds.")

    return successful, failed, mismatched

if __name__ == "__main__":
    if len(sys.argv) != 3 and (len(sys.argv) != 4 or sys.argv[3] != "-v"):
        print("Usage:\npython3 a1test.py aX.py assignmentX-public-tests.txt [-v]")
        sys.exit()

    verbose = len(sys.argv) == 4 and sys.argv[3] == "-v"

    if not os.path.isfile(sys.argv[1]):
        print("File '" + sys.argv[1] + "' not found.")
        sys.exit()
    if not os.path.isfile(sys.argv[2]):
        print("File '" + sys.argv[2] + "' not found.")
        sys.exit()

    try:
        proc = subprocess.Popen(["python3", sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    except Exception as e:
        print("Failed to start " + sys.argv[1])
        print("Error:")
        print(e)
        sys.exit()
    
    tests = file_to_tests(sys.argv[2])

    test_process(proc, tests, verbose, True)
    proc.terminate()
