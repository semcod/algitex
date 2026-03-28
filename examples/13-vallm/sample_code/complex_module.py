
def process_data(data):
    """Process data with nested logic."""
    result = []
    for item in data:
        if item:
            if isinstance(item, dict):
                if 'value' in item:
                    if item['value'] > 0:
                        for sub in item['items']:
                            if sub.valid:
                                result.append(sub.process())
    return result

def calculate(x, y, operation):
    if operation == "add":
        return x + y
    elif operation == "sub":
        return x - y
    elif operation == "mul":
        return x * y
    elif operation == "div":
        if y != 0:
            return x / y
        else:
            return None
    else:
        return None
