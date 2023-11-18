from utils.args import parser
from utils.simulation import Scenario, Bot, Package


def main():
    # Parse command line arguments
    args = vars(parser.parse_args())
    print(args)

    if args.get("subcmd") == "term":
        Scenario.from_name(args["scenario"])

    # Get scenario


if __name__ == "__main__":
    main()
