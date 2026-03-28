# Sample code with issues for BatchFix demo
# This file has string concatenation issues

def greet(name):
    # Issue: String concatenation can be converted to f-string
    return "Hello, " + name + "!"

def format_price(amount, currency):
    # Issue: String concatenation can be converted to f-string  
    return str(amount) + " " + currency

def build_path(base, filename):
    # Issue: String concatenation can be converted to f-string
    return base + "/" + filename

if __name__ == "__main__":
    print(greet("World"))
    print(format_price(100, "USD"))
    print(build_path("/home", "file.txt"))
