from fermat import *
from linear_congruential import *

from time import time

qtt_numbers = 10

lengths = [40, 56, 80, 128, 168, 224, 256, 512, 1024, 2048, 4096]

file = open("output.txt", 'w+')

start_time = time()

for n_bits in lengths:
    print("Initializing:", n_bits)
    content = f"{n_bits} bits \n\n"
    
    # Create a generator with n bits
    generator = generator_linear_congruential(n_bits)

    # Generate qtt_numbers for each length
    for j in range(qtt_numbers):
        print("Range:", j)

        # Generate a number
        number = next(generator)

        # Repeat until a prime number has not been found
        while number % 2 == 0 or fermat(number) == False:
            
            # Generate another number
            number = next(generator)

        content += f"{number}\n"

    content += "\n" + "-" * 50 + "\n"
    file.write(content)

file.write(f"\nExecution time: {start_time - time()}")
file.close()
