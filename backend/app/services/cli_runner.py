from typing import Tuple
import anyio
import logging

logger = logging.getLogger(__name__)


class CliInstance:
    def __init__(self):
        self.commands = []
        self.timeout = 300

    def add_arg(self, *args: str):
        self.commands.extend(args)

    async def run(self) -> Tuple[str, str, int]:
        commands = self.commands
        # timeout = self.timeout

        proc = await anyio.run_process(commands, check=False)
        if proc.returncode:
            logger.error(f"{' '.join(commands)}")
        return (
            proc.stdout.decode().strip(),
            proc.stderr.decode().strip(),
            proc.returncode or 0,
        )
