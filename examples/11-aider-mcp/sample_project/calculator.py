
def calc(a,b,op):
    if op=="+":
        return a+b
    elif op=="-":
        return a-b
    elif op=="*":
        return a*b
    elif op=="/":
        if b==0:
            return None
        return a/b
    else:
        return None
