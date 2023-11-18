from utils.args import parser
from utils.simulation import Scenario, BOT_SPEED
import datetime 


def printOutput (scenario:Scenario) -> None:
    t1 = datetime.datetime(year=2023, month=11, day =18, hour=7, minute=0, second=0)
    outputFile = open("output.txt", "w+")
    i=0
    totalDistance = 0
    lastDeliveryTime = 0
    for bot in scenario.bots: 
        botDistance  =  (bot.accumulated_cost -2*bot.num_deliveries)*BOT_SPEED
        outputFile.write(f"Bot {i}: \n\t Total Running Time: {bot.accumulated_cost:.2f} \n\t Number of Deliveries: {bot.num_deliveries} \n\t Total Distance Travelled: {botDistance:.2f}\r" )
        if (bot.accumulated_cost > lastDeliveryTime):
            lastDeliveryTime=bot.accumulated_cost
        totalDistance += botDistance
    
    outputFile.write(f"Summary: \n\t Total Distance: {totalDistance:.2f}, \n\t Total End Time: {datetime.timedelta(hours=int(lastDeliveryTime))+t1}" )
    outputFile.close()



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
        
        printOutput(scenario)




if __name__ == "__main__":
    main()
