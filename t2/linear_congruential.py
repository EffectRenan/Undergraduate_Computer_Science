def linear_congruential(m, a, c, previous):
	return ((previous * a) + c) % m

def generator_linear_congruential(length):

    # Seed value
    x0 = 3

    # Modulus parameter
    m = 2 ** (length) - 1

    # Multiplier term
    a = 3

    # Increment term
    c = 1

    # Initializing with x0
    previous = x0

    while True:
        # add m for a min of: 2^(n) - 1 
        previous = m + linear_congruential(m, a, c, previous) 
        yield previous


from time import time


if __name__ == '__main__':
    qtt = 10000000

    lengths = [40, 56, 80, 128, 168, 224, 256, 512, 1024, 2048, 4096]

    for n_bits in lengths:
        start_time = time()
        generator = generator_linear_congruential(n_bits)

        for j in range(qtt):
            next(generator)
        
        print(f"{n_bits} bits: {time() - start_time} seconds") 


