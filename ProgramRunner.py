from Runner import Runner
from typing import Union, List
import subprocess


class ProgramRunner(Runner):
    """Test a program with inputs."""

    def __init__(self, program: Union[str, List[str]]) -> None:
        """
        Initialize
        'program' is a program spec as passed to 'subprocess.run()'    
        """
        self.program = program

    def run_process(self, inp: str = "") -> subprocess.CompletedProcess:
        """
        Run the program with 'inp' as input.
        Return the result of 'subprocess.run()'.
        """
        return subprocess.run(self.program,
                                inputs=inp,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)

    def run(self, inp: str = ""):
        """
        Run the program with 'inp' as input,
        Return test outcome based on result of 'subprocess.run()'
        """
        result = self.run_process(inp)

        if result.returncode == 0:
            outcome = self.PASS
        elif result.returncode < 0:
            outcome = self.FAIL
        else:
            outcome = self.UNRESOLVED

        return (result, outcome)

    
    
