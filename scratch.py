

try:
    myFunction(0)
except:
    print 'man you messed up!'

print 'do i still get here?'


def myFunction(foo):

    foo += 1

    return(foo)
