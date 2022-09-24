from time import time

# Euclides
def gcd(a, b): 
    if a == 0 :
        return b 
      
    return gcd(b % a, a)

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

def fermat(n):

    # k: times
    k = 1000

    for i in range(k):
        # Step 1
        # Pick an a: 1 < a < n - 1
       
        a = get_an_a(n)

        # Step 2
        # Check gcd != 1

        if gcd(a, n) != 1:
            return False

        # Step 3
        # Check a ^ (n - 1) = 1 mod (n)

        if power(a, n - 1, n) != 1:
            return False

    return True
