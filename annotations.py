#!/usr/bin/env python3

import pandas as pd
import argparse
import os

def replace_name(name):
    entities = pd.read_csv('data/rezojdm16k/originals/entities_originals.csv', sep='\t', names=['id', 'name'])
    ent_map = dict(zip(entities['id'].tolist(), entities['name'].tolist()))

    raff = name.split('>')
    for j in range(1, len(raff)):
        raff[j] = ent_map[int(raff[j])]

    raff = '>'.join(raff)

    # hs = pd.concat([batches[0], batches[1], batches[2]])
    # hs['Obj Nm'] = hs['Obj Nm'].map(replace_name)
    # hs['Sub Nm'] = hs['Sub Nm'].map(replace_name)

    return raff

def get_batches(dataset):
    df = pd.read_csv(f"predictions/{args.dataset}_all_preds.csv", sep='\t')

    if dataset == 'rezojdm16k':
        df = df.loc[(df['Short. Path.'] >= 3) & (df['Sub Nm'] != df['Obj Nm'])]
        dfs = []
    elif dataset == 'rlf27k':
        df = df.loc[(df['Sub Nm'] != df['Obj Nm']) & (df['Short. Path.'] == float('inf'))]
        dfs = []

    for i in range(0, 10):
        dfs.append(df.loc[(df['Conf'] > i/10) & (df['Conf'] <= i/10+0.1)])
        dfs[i] = dfs[i].sample(frac=1, random_state=42)

    batches = []
    for batch_i in range(0,6):
        list_temp = []
        for j in range(0,10):
            list_temp.append(dfs[j].iloc[batch_i*4: batch_i*4+4])
        batches.append(pd.concat(list_temp)[['Sub Nm', "Rel Nm", "Obj Nm"]].sample(frac=1, random_state=42))

    if not os.path.exists('annotations/batches'):
        os.makedirs("annotations/batches")

    pd.concat([batches[0], batches[1], batches[2]]).to_csv(f"annotations/batches/A1_{dataset}.tsv", sep="\t")
    pd.concat([batches[0], batches[3], batches[4]]).to_csv(f"annotations/batches/A2_{dataset}.tsv", sep="\t")
    pd.concat([batches[1], batches[3], batches[5]]).to_csv(f"annotations/batches/A3_{dataset}.tsv", sep="\t")
    pd.concat([batches[2], batches[4], batches[5]]).to_csv(f"annotations/batches/A4_{dataset}.tsv", sep="\t")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parser For Arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-dataset', dest='dataset', type=str, default="rezojdm16k", help='Dataset to use, default: rezojdm16k')

    args = parser.parse_args()

    get_batches(dataset=args.dataset)
