from os import popen
from re import sub
import subprocess
import argparse
import pickle
from fuzzer.csv_mutation_fuzzer import CsvMutationFuzzer

if __name__ == "__main__":
    # add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", nargs=2, help="binary to fuzz")
    args = parser.parse_args()
    # get basename
    txt_name = args.binary[1].split('/')[-1].split('.')[0]
    # reed seeds
    with open(args.binary[1], 'rb') as f:
        seed = f.read()
    # prepare fuzzer
    fuzzer = CsvMutationFuzzer(seed)
    # run the main loop
    # TODO: connect to gdb with pwntools
    for i in range(1000):
        process = subprocess.Popen(args.binary[0],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        # get input
        input_bytes = next(fuzzer)
        # print(input_bytes, end = ' | ')
        try:
            # send input and check return code
            outs, err = process.communicate(input_bytes, timeout=0.1)
            print(f"{i}: PASSED", end=" | ")
            print(
                f"input_len = {hex(len(input_bytes))} outs = {outs}, err = {err}, exitcode = {process.returncode}"
            )
            if process.returncode == -11:  #SIGFAULT -> throws exception
                raise subprocess.CalledProcessError(process.returncode,
                                                    args.binary[0])
        # if seg fault, break the loop
        except subprocess.CalledProcessError as e:
            print(f"{i}: Crashed")
            with open(f'{txt_name}_crash.txt', 'wb') as f:
                print(input_bytes)
                pickle.dump(input_bytes, f)
                break

        except subprocess.TimeoutExpired as er:
            print(f"{i}: Timeout")
            with open(f'csv_timeout_{i}.pkl', 'wb') as f:
                pickle.dump(input_bytes, f)
