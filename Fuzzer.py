from Runner import Runner
from PrintRunner import PrintRunner


class Fuzzer:
    """base class for fuzzers."""

    def __init__(self) -> None:
        """Constructor"""
        pass

    def fuzz(self) -> str:
        """Return fuzz input"""
        return ""

    def run(self, runner: Runner = Runner()):
        """Run runner with fuzz input"""
        return runner.run(self.fuzz())

    def runs(self, runner: Runner = PrintRunner(), trials: int = 10):
        """Run 'runner' with fuzz input, 'trials' times"""
        return [self.run(runner) for i in range(trials)]