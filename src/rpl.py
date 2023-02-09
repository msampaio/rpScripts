import argparse
import os
import pandas


def parse_txt(txt_fname):
    with open(txt_fname, 'r') as fp:
        rows = [row.rstrip('\n') for row in fp.readlines() if row]

    dics = []
    for row in rows:
        label, ind = row.split(',')
        label = label.lstrip().rstrip()
        ind = ind.lstrip().rstrip()
        dics.append({
            'label': label,
            'index': ind,
        })

    return dics


def main(csv_fname, txt_fname):
    labels = parse_txt(txt_fname)
    df = pandas.read_csv(csv_fname)

    df['Label'] = pandas.Series([None] * len(df))

    for dic in labels:
        ind = df[df.Index==dic['index']].index[0]
        df.loc[ind, 'Label'] = dic['label']

    df['Label'] = df.Label.fillna(method='ffill')
    path = os.path.splitext(csv_fname)[0] + '-labelled.csv'
    df.to_csv(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'rpp',
                    description = "Annotate RPC's CSV output with labels.",
                    epilog = 'Rhythmic Partitioning Labeller')

    parser.add_argument("-c", "--csv", help = "CSV filename.")
    parser.add_argument("-t", "--txt", help = "TXT labelling schema.")

    args = parser.parse_args()
    csv_fname = args.csv
    txt_fname = args.txt

    print('Running script on {} filename...'.format(csv_fname))

    main(csv_fname, txt_fname)