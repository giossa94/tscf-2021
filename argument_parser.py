import argparse

def get_argument_parser():
    parser = argparse.ArgumentParser(description="Read topology configuration")
    parser.add_argument(
        "-k",
        action="store",
        type=int,
        default=4,
        required=False,
        help="K that defines the Fat Tree.",
    )
    parser.add_argument(
        "-p",
        "-number_of_planes",
        action="store",
        type=int,
        default=None,
        required=False,
        help="Number of planes in the Fat Tree.",
    )
    parser.add_argument(
        "-c",
        "-clean_lab",
        action="store",
        type=bool,
        default=True,
        required=False,
        help="Run kathara lclean before starting emulation.",
    )
    parser.add_argument(
        "-w",
        "-window_size",
        action="store",
        type=int,
        default=10,
        required=False,
        help="Number of packets considered in a window.",
    )
    parser.add_argument(
        "-t",
        "-threshold",
        action="store",
        type=float,
        default=0.2,
        required=False,
        help="Threshold for the sliding window check.",
    )
    return parser
