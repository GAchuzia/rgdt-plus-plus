from utils.args import parser
from utils.simulation import Scenario


def main():
    # Parse command line arguments
    args = vars(parser.parse_args())
    print(args)

    # Get scenario
    if args.get("subcmd") == "term":
        scenario = Scenario.from_name(args["scenario"])

    # Main loop
    for bot in scenario.bots:
        print(bot)


if __name__ == "__main__":
    main()
