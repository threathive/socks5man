

x = 0

def a():
    global x
    if x:
        print "asd"
    else:
        print "1"

a()
x = "l"
a()