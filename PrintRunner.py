from Runner import Runner
from typing import Any


class PrintRunner(Runner):
    """Simple runner, printing the input"""

    def run(self, inp) -> Any:
        """Print the given input"""
        print(inp)
        return (inp, Runner.UNRESOLVED)
