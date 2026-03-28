# Sample code with magic number issues
# This file has magic number issues

def connect():
    # Issue: Magic number: 30 - use named constant
    timeout = 30
    return timeout

def retry():
    # Issue: Magic number: 3 - use named constant
    attempts = 3
    return attempts

def calculate():
    # Issue: Magic number: 100 - use named constant
    result = 100 * 2
    return result

if __name__ == "__main__":
    print(connect())
    print(retry())
    print(calculate())
