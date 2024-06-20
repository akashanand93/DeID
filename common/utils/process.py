from dataclasses import dataclass
import hashlib
from pathlib import Path
import random
from typing import List
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
from common.utils.base import AsyncUtils


@dataclass
class ShellTask:
    """
    Represents a set of shell commands to run.
    """

    title: str
    commands: List[str]
    parallelize: bool = False
    sensitive: bool = False  # command  is not logged


class Shell:
    """
    A collection of shell command utilities.
    """

    @staticmethod
    def run_cmd_blocking(cmd_raw: str) -> int:
        """
        Wrapper over the async run_cmd.
        """
        run_cmd_blocking = AsyncUtils.sync_wrapper(Shell.run_cmd)
        return run_cmd_blocking(cmd_raw)

    @staticmethod
    async def run_cmd(cmd_raw: str) -> int | None:
        """
        AsyncIO wrapper for running a shell command with stdout/stderr piped to the console.
        Returns the exit code from the given command.
        """
        proc = await asyncio.create_subprocess_shell(
            cmd_raw,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ,
        )

        async def stream_output(stream, callback):
            while True:
                line = await stream.readline()
                if line:
                    callback(line.decode().strip())
                else:
                    break

        await asyncio.gather(
            stream_output(proc.stdout, logger.debug),
            stream_output(proc.stderr, logger.info),
        )

        await proc.wait()
        return proc.returncode

    @staticmethod
    async def execute(task: ShellTask) -> List[int | None]:
        """
        Executes the given ShellTask.
        If parallelize is True, runs all commands concurrently.
        If parallelize is False, runs all commands sequentially.

        Returns the exit codes of the commands.
        """
        logger.debug("---------------------------------------------------------")
        logger.info(task.title)
        if task.parallelize:
            logger.warning(f"Executing {len(task.commands)} commands in parallel")
            for cmd in task.commands:
                cmd_str = "REDACTED" if task.sensitive else cmd
                logger.warning(f"Executing command: {cmd_str}")

            # Run commands concurrently
            executors = [Shell.run_cmd(cmd) for cmd in task.commands]
            return await asyncio.gather(*executors)
        # ---
        exit_codes = []
        for cmd in task.commands:
            cmd_str = "REDACTED" if task.sensitive else cmd
            logger.warning(f"Executing command: {cmd_str}")
            exit_codes.append(await Shell.run_cmd(cmd))

        return exit_codes

    @staticmethod
    def load_env_files(env_files: List[Path]) -> None:
        """Loads the given .env files into the environment."""
        for env_file in env_files:
            load_dotenv(env_file)


# TODO: Bundle the functions below to a Math module.
def decide(probability) -> bool:
    """A convenience function"""
    return random.random() < probability


def deterministic_random(string: str, start=1, end=100) -> int:
    """
    Hashes the given string & returns a deterministic random int in the range.
    """
    seed = int(hashlib.sha256(string.encode("utf-8")).hexdigest(), 16)
    random.seed(seed)
    return random.randint(start, end)


if __name__ == "__main__":
    # QA:
    uuid = "123e4567-e89b-12d3-a456-426614174000"
    print(deterministic_random(uuid))
    print(random.randint(2, 100))
    print(deterministic_random(uuid))
