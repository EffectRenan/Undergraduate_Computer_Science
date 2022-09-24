def xorshift32(m, previous):
    previous ^= previous << 13
    previous ^= previous >> 17
    previous ^= previous << 5
    return  previous % m 

def generator_xorshift(length):
    # Seed value
    x0 = 3

    # Modulus parameter
    m = 2 ** (length) - 1

    # Initializing with x0
    previous = x0

    while True:
        previous = m + xorshift32(m, previous)
        yield previous


from time import time

if __name__ == '__main__':
    qtt = 10000000

    lengths = [40, 56, 80, 128, 168, 224, 256, 512, 1024, 2048, 4096]

    for n_bits in lengths:
        start_time = time()
        generator = generator_xorshift(n_bits)

        for j in range(qtt):
            next(generator)
        
        print(f"{n_bits} bits: {time() - start_time} seconds") 

