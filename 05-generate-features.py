import pandas as pd
import sys

def main(in_dir1, in_dir2, out_dir1, out_dir2):
    fight_data = pd.read_csv(in_dir1)
    fighter_data = pd.read_csv(in_dir2)

    # TODO: calculate averages for fight stats

    # TODO: use for calculating elo
    # for _, fighter in fighter_data.iterrows():
    #     print(fighter)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])