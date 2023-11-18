from utils.args import parser
from utils.simulation import Scenario


def main():
    # Parse command line arguments
    args = vars(parser.parse_args())

    # Get scenario
    if args.get("subcmd") == "term":
        scenario = Scenario.from_name(args["scenario"])

        # Main loop
        while not scenario.complete():
            for bot in scenario.bots:
                destination_node = bot.calculate_destination(scenario)
                bot.step_towards(destination_node, scenario)
        print("Simulation complete.")
        for bot in scenario.bots:
            print(bot.accumulated_cost)


if __name__ == "__main__":
    main()
