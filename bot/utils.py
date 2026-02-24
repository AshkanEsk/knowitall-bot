"""Utility functions for the bot."""

import logging
import os
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level
    )


class SingleInstanceLock:
    """Ensure only one instance of the bot runs."""
    
    def __init__(self, lock_file: str = "bot.lock"):
        self.lock_file = lock_file
        self.fd = None
    
    def __enter__(self):
        if sys.platform == 'win32':
            # Windows implementation
            import msvcrt
            try:
                self.fd = open(self.lock_file, 'w')
                msvcrt.locking(self.fd.fileno(), msvcrt.LK_NBLCK, 1)
            except (IOError, OSError):
                raise RuntimeError(
                    "Another bot instance is already running! "
                    "Please stop it first."
                )
        else:
            # Unix implementation
            import fcntl
            self.fd = open(self.lock_file, 'w')
            try:
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                raise RuntimeError(
                    "Another bot instance is already running! "
                    "Please stop it first."
                )
        return self
    
    def __exit__(self, *args):
        if self.fd:
            self.fd.close()
            try:
                os.remove(self.lock_file)
            except OSError:
                pass