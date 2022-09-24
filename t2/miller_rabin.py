from time import time

def get_an_a(n):
    # Get an "a" based on timestamp to use as a "random" number

    timestamp = time() # Example 1639508236.2790089

    # Remove dot
    # Example 16395082362790089
    str_timestamp = str(timestamp)
    index = str_timestamp.index(".")
    timestamp = int(str_timestamp[:index] + str_timestamp[index+1:])

    # a: 1 < a < n - 1
    return 1 + timestamp % (n - 2)

# Modular exponentiation
# to work with larger numbers
def power(x, y, p):
     
    # Initialize result
    res = 1;
     
    # Update x if it is more than or
    # equal to p
    x = x % p;
    while (y > 0):
         
        # If y is odd, multiply
        # x with result
        if (y & 1):
            res = (res * x) % p;
 
        # y must be even now
        y = y>>1; # y = y/2
        x = (x * x) % p;
     
    return res;

def miller_rabin(n):

    # Step 1
    # n - 1 = 2^k * m

    n_1 = n - 1
    k = 0

    while n_1 % (2 ** (k + 1)) == 0:
        k += 1

    m = int(n_1 / (2 ** k))

    # Step 2
    # Pick an a: 1 < a < n - 1

    a = get_an_a(n)

    # Step 3
    # b = a ^ m mod n
    # Probably prime: b = -1, b == n - 1
    # Composite: b = 1

    b = power(a, m, n)

    if b != 1 and b != n_1:

        # Step 4

        # Keep squaring x while one
        # of the following does not happen

        while k < n_1 and b != 1 and b != n_1:
            b = (b * b) % n
            k *= 2

    return b == -1 or b == n_1
