import argparse
import os

parser = argparse.ArgumentParser(
    prog="rgdt++",
    description="Command line utility for finding the shortest delivery path for RGTD Ltd.",
    epilog="This program is licensed under the MIT license.",
)

subparsers = parser.add_subparsers()
term = subparsers.add_parser(
    "term", description="Command for running utility in the command line interface."
)

# Terminal commands


def ValidScenario(name: str) -> str:
    """Check if a provided scenario name has both a .json and .xml file associated with it."""

    if not os.path.exists(f"{name}.xml"):
        raise argparse.ArgumentTypeError(f"Scenario '{name}' does not have an assoicated XML file.")

    if not os.path.exists(f"{name}.json"):
        raise argparse.ArgumentTypeError(f"Scenario case '{name}' does not have an assoicated JSON file.")

    return name


term.add_argument(
    "scenario",
    type=ValidScenario,
)
