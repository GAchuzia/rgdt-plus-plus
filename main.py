from utils.args import parser
from utils.simulation import Scenario, BOT_SPEED, DELIVERY_TIME
import datetime


def print_output(scenario: Scenario) -> None:
    """Prints the output text file required by the competition rules."""
    t1 = datetime.datetime(year=2023, month=11, day=18, hour=7, minute=0, second=0)
    output_file = open("output.txt", "w+")
    total_distance = 0
    last_delivery_time = 0

    for bot in scenario.bots:
        bot_distance = (bot.accumulated_cost - DELIVERY_TIME * bot.num_deliveries) * BOT_SPEED
        output_file.write(f"Bot {bot.id}: \n")
        output_file.write(f"\tTotal Running Time: {bot.accumulated_cost:.2f}\n")
        output_file.write(f"\tNumber of Deliveries: {bot.num_deliveries}\n")
        output_file.write(f"\tTotal Distance Travelled: {bot_distance:.2f}\n")

        if bot.accumulated_cost > last_delivery_time:
            last_delivery_time = bot.accumulated_cost
        total_distance += bot_distance

    output_file.write("Summary:\n")
    output_file.write(f"\tTotal Distance: {total_distance:.2f}\n")
    output_file.write(f"\tTotal End Time: {datetime.timedelta(hours=int(last_delivery_time))+t1}\n")
    output_file.close()


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

        print_output(scenario)


if __name__ == "__main__":
    main()
