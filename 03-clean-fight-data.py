import pandas as pd
import sys

def main(in_dir, out_dir):
    df = pd.read_csv(in_dir)

    print(df)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])