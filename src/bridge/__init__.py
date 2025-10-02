"""
Bridge URL - CLI tool for managing Netlify URL redirections.

A Python CLI tool that reads rule-based JSON configuration files,
validates and expands hosts, converts regex paths to Netlify patterns,
and generates deployment artifacts for Netlify redirections.
"""

__version__ = "0.1.0"
__author__ = "Arkady"
__email__ = "arkady@example.com"

from .cli import main
from .core import HostExpander, RuleProcessor

__all__ = ["HostExpander", "RuleProcessor", "main"]