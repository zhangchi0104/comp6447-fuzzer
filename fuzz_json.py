import json
import random
import time
from pwn import *
import os
import sys
import subprocess

def bitFlip(sampleInputFile, binary):

    print("Flipping random bits in sample input...\n", end="")

    sampleInputFile.seek(0)
    sampleInput = sampleInputFile.read()

    for _ in range(0, 500):

        # convert the input into a bytearray
        b = bytearray(sampleInput, 'UTF-8')

        # Then we search through the entire bytearray created, and randomly
        # flip some of the bits
        for i in range(0, len(b)):
            if random.randint(0, 20) == 1:
                b[i] ^= random.getrandbits(7)

        # Once we have flipped the bits, we want to decode this back into a string
        # that can be passed in as input to the binary
        mutatedInput = b.decode('ascii').strip()

        if checker(binary, mutatedInput):
            print("Found vulnerability from bit flip!")
            return True
    return False

def checker(binary, mutatedInput):

    p = process(binary)
    p.sendline(mutatedInput)
    p.proc.stdin.close()

    exit_status = None
    while exit_status == None:
        p.wait()
        exit_status = p.returncode
    p.close()

    # After it has finished running, we check the exit status of the process.
    # If this input resulted in an exit status less than 0 (and also didn't abort),
    # this means there was an exception, so we want to write it to 'bad.txt'
    # and exit the fuzzer.
    if exit_status < 0 and exit_status != -6:
        res = open("bad.txt", "w+")
        res.write(mutatedInput)
        res.close()
        return True
    return False