from os import PathLike
from argparse import ArgumentParser
import pwn
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

    def __init__(self, binary: PathLike, seed: PathLike):
        self._binary = binary
        self._current_checkpoint = 0
        f = open(seed, 'rb')
        seed_content = f.read()
        seed_type = infer_type(seed_content)
        log.info(f"Detected seed with filetype '{seed_type}'")

        self._binary = pwn.gdb.debug(binary)
        print(self._binary.proc.pid)
        self._binary.interactive()
        self._fuzzer = FUZZERS_BY_TYPE[seed_type](seed_content)
        self._read_until_next_prompt()
        # setup breakpoints
        self._break('main')
        self._break('_fini')
        # attach to process jump back to main
        self._gdb.sendline(f'attach {str(self._binary.proc.pid)}'.encode())
        self._read_until_next_prompt()
        self._gdb.interactive()
        # setup checkpoint
        self._current_checkpoint = self._checkpoint()
        self._continue()

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

    def _reset(self):
        """
        Recover from forked checkpoint and make new checkpoints
        """
        cmd = f"restart {self._current_checkpoint}"
        self._gdb.sendline(cmd.encode())

        self._read_until_next_prompt()
        if (self._current_checkpoint - 1 != 0):
            del_cmd = f"delete checkpoint {self._current_checkpoint - 1}"
            self._gdb.sendline(del_cmd.encode())
            self._read_until_next_prompt()

        self._current_checkpoint = self._checkpoint()
        log.info(f"Rewinding to checkpoint {self._current_checkpoint - 1}")

    def start(self, n_runs=500):
        log.info(f"start fuzzing for {n_runs} times")
        inputs = next(self._fuzzer)
        print(len(inputs))
        self._binary.send(inputs)
        self._gdb.interactive()

    def _jump(self, position: str):
        self._gdb.sendline(f'jump {position}'.encode())
        self._read_until_next_prompt()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("args", nargs=2)
    args = parser.parse_args()
    binary, seed = args.args

    runner = Harness(binary, seed)
    runner.start()
