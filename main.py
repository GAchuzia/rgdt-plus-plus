from utils.args import parser


def main():

    # Parse command line arguments
    args = vars(parser.parse_args())


if __name__ == "__main__":
    main()
