from ProgramRunner import ProgramRunner
import subprocess


class BinaryProgramRunner(ProgramRunner):
    def run_process(self, inp: str = "") -> subprocess.CompletedProcess:
        """
        Run the program with 'inp' as input.
        Return result of 'subprocess.run()'
        """
        return subprocess.run(self.program,
                                input=inp.encode(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)