"""
Create a Judge Metadata file for the project based on the Federal Judicial
Center's Biographical Directory of Article III Federal Judges, 1789-present.

Use the commission centered (Federal Judicial Service) table available at:

- https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export

Processing notes:

- If there is no appointing judge if there is new commission or appointment,
  use the party of the previous commission's appointing president.
- Transform USCA into codes: 1-11; FC (Federal Circuit); CIT (Court of
  International Trade); and, DC (DC Circuit).
- Replaces `,` with `<` in the names of the judges for further processing.
"""

import argparse
import csv
import logging
import re


court_map = {
    'U.S. Court of Appeals for the District of Columbia Circuit': 'DC',
    'U.S. Court of Appeals for the Eighth Circuit': '8',
    'U.S. Court of Appeals for the Eleventh Circuit': '11',
    'U.S. Court of Appeals for the Federal Circuit': 'FC',
    'U.S. Court of Appeals for the Fifth Circuit': '5',
    'U.S. Court of Appeals for the First Circuit': '1',
    'U.S. Court of Appeals for the Fourth Circuit': '4',
    'U.S. Court of Appeals for the Ninth Circuit': '9',
    'U.S. Court of Appeals for the Second Circuit': '2',
    'U.S. Court of Appeals for the Seventh Circuit': '7',
    'U.S. Court of Appeals for the Sixth Circuit': '6',
    'U.S. Court of Appeals for the Tenth Circuit': '10',
    'U.S. Court of Appeals for the Third Circuit': '3',
    'U.S. Court of International Trade': 'CIT'
}


def main(args):
    fjc_csv = csv.DictReader(open(args.input, newline=''))
    judge = {}
    fieldnames = ['Judge', 'Circuit', 'Party', 'StartYear', 'EndYear']
    out_csv = csv.DictWriter(open(args.output, 'w', newline=''),
        fieldnames=fieldnames, extrasaction="ignore")
    out_csv.writeheader()
    previous_commission = { 'Judge': ''}

    for row in fjc_csv:
        commission = {}
        # replace comma with '<' based on previous projects processing
        commission['Judge'] = row['Judge Name'].replace(",", "<")
        seat_id = row['Seat ID']
        commission['SeatID'] = seat_id
        commission['Circuit'] = court_map.get(row['Court Name'], '')
        # handle appointing president party if its a move (5th to 11th)
        if re.search('^None', row['Party of Appointing President']) or \
                len(row['Party of Appointing President']) == 0:
            if previous_commission['Judge'] == commission['Judge']:
                commission['Party'] = previous_commission['Party']
            else:
                commission['Party'] = row['Party of Appointing President']
        else:
            commission['Party'] = row['Party of Appointing President']
        commission['StartYear'] = row['Commission Date']
        commission['EndYear'] = row['Termination Date']
        previous_commission = commission
        if len(commission['Circuit']) > 0:
            out_csv.writerow(commission)


def setup_logging(args):
    """Set up basic logging with default in args to sys.stdout"""
    logformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    loglevel = getattr(logging, args.loglevel.upper())
    formatter = logging.Formatter(logformat)
    if args.verbose is True:
        loglevel = logging.INFO
    if args.debug is True:
        loglevel = logging.DEBUG
    logging.basicConfig(format=logformat, level=loglevel)

    if args.verbose is False and args.debug is False:
        logging.getLogger().handlers.pop()

    if args.logfile:
        loghandler = logging.handlers.RotatingFileHandler(
            filename=args.logfile,
            maxBytes=1024*1024*5,
            backupCount=5)
        loghandler.setFormatter(formatter)
        loghandler.setLevel(loglevel)
        logging.getLogger().addHandler(loghandler)
    return


def parse_args():
    """Load command line arguments"""
    parser = argparse.ArgumentParser(description='Create a table of CA commissions')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print some diagnostic information")
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help="debug output")
    parser.add_argument('-l', '--logfile', help="Optional logfile")
    parser.add_argument('-L', '--loglevel',
                        default='WARNING', help="Python logging levels")
    parser.add_argument('input', help='csv input file')
    parser.add_argument('output', help="csv output")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args)
    main(args)
