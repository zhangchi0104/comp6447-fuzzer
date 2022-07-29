import subprocess
from os import PathLike
from argparse import ArgumentParser
from pwn import log, PTY
import mutators
from file_type import infer_type

FUZZERS_BY_TYPE = {
    "csv": mutators.CsvMutator,
    "json": mutators.jsonMutationFuzzer
}

# pwn.context.log_level = 'debug'


class Harness(object):
    TIMEOUT = 1
    EXITCODES = {
        1: "SIGHUP",
        2: "SIGINT",
        3: "SIGQUIT",
        4: "SIGILL",
        5: "SIGTRAP",
        6: "SIGABRT",
        7: "SIGBUS",
        8: "SIGFPE",
        9: "SIGKILL",
        10: "SIGUSR1",
        11: "SIGEGV (Segmentation fault)",
        12: "SIGUSR2",
        13: "SIGPIPE",
        14: "SIGALRM",
        15: "SIGTERM",
        16: "SIGSTKFLT",
        17: "SIGCHLD",
        18: "SIGCONT",
        19: "SIGSTOP",
        20: "SIGTSTP",
        21: "SIGTTIN",
        22: "SIGTTOU",
        23: "SIGURG",
        24: "SIGXCPU",
        25: "SIGXFSZ",
        26: "SIGVTALRM",
        27: "SIGPROF",
        28: "SIGWINCH",
        29: "SIGIO",
        30: "SIGPWR",
        31: "SIGSYS",
    }

    def __init__(self, binary: PathLike, seed: PathLike):
        self._binary_path = binary
        self._current_checkpoint = 0
        f = open(seed, 'rb')
        seed_content = f.read()
        f.close()
        seed_type = infer_type(seed_content)
        log.info(f"Detected seed with filetype '{seed_type}'")

        self._binary_process = subprocess.Popen(self._binary_path,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE)

        self._fuzzer = FUZZERS_BY_TYPE[seed_type](seed_content)

    """
    def _read_until_next_prompt(self):
        self._gdb.recvuntil(b'pwndbg> ', drop=True, timeout=self.TIMEOUT)

    def _break(self, position: str = ""):
        self._gdb.sendline(f'b {position}'.encode())
        log.info(b'sent: ' + f'b {position}'.encode())
        self._gdb.recvuntil(b'Breakpoint ', drop=True, timeout=self.TIMEOUT)
        breakpoint = self._gdb.recvuntil(b' ', drop=True, timeout=self.TIMEOUT)
        breakpoint = int(breakpoint.decode())
        log.info(f"New breakpoint @ {position}")
        self._read_until_next_prompt()
        return breakpoint

    def _checkpoint(self):
        self._gdb.sendline(b'checkpoint')
        self._gdb.recvuntil(b'checkpoint ', drop=True, timeout=self.TIMEOUT)
        checkpoint = self._gdb.recvuntil(b': ',
                                         drop=True,
                                         timeout=self.TIMEOUT)
        checkpoint = int(checkpoint.decode())
        log.info(f"New checkpoint {checkpoint}")
        self._read_until_next_prompt()
        return checkpoint

    def _continue(self):
        log.info("Continuing")
        self._gdb.sendline(b"continue")
        self._gdb.recvuntil(b'Continuing.', drop=True, timeout=self.TIMEOUT)
        
    def _jump(self, position: str):
        self._gdb.sendline(f'jump {position}'.encode())
        self._read_until_next_prompt()
    """

    def _reset(self):
        """
        Recover from forked checkpoint and make new checkpoints
        """
        self._binary_process = subprocess.Popen(self._binary_path,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE)

    def start(self, n_runs=500):
        txt_name = self._binary_path.split('/')[-1].split('.')[0]
        for i in range(n_runs):

            # get input
            input_bytes = next(self._fuzzer)
            # print(input_bytes, end = ' | ')
            try:
                # send input and check return code
                outs, err = self._binary_process.communicate(input_bytes,
                                                             timeout=0.1)
                exitcode = self._binary_process.returncode
                if exitcode >= 0:
                    print(f"{i}: PASSED | ", end="")
                    print(f"exitcode: {exitcode}")
                    print("=" * 40)
                    print(f"\tinput_len = {hex(len(input_bytes))}")
                    print(f"\tstdout = {outs}")
                    print(f"\tstderr = {err}")

                else:  #SIGFAULT -> throws exception
                    raise subprocess.CalledProcessError(
                        self._binary_process.returncode, self._binary_path)
            # if seg fault, break the loop
            except subprocess.CalledProcessError as e:
                print(f"Program Crashed: exitcode = {exitcode}")
                print(f"\tReason: {self.EXITCODES[-exitcode]}")
                print(
                    f"Written input crashed the program to {txt_name}-crashed.txt"
                )
                with open(f'{txt_name}_crash.txt', 'wb') as f:
                    f.write(input_bytes)
                    break

            except subprocess.TimeoutExpired as er:
                print(f"{i}: Timeout")
                with open(f'csv_timeout_{i}.pkl', 'wb') as f:
                    f.write(input_bytes)
            self._reset()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("args", nargs=2)
    args = parser.parse_args()
    binary, seed = args.args

    runner = Harness(binary, seed)
    runner.start()
