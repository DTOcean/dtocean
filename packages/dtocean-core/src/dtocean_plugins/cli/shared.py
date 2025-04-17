import argparse


class SmartFormatter(argparse.HelpFormatter):
    # https://stackoverflow.com/a/22157136/3215152

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)
