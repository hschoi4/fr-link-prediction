#!/usr/bin/env python3

import numpy as np
import pandas as pd
import collections
import dataclasses
from typing import Set, Any
import argparse
from random import randint

@dataclasses.dataclass
class triples:
    train: Any
    valid: Any
    test: Any

def filter_set(df, train):
    train_ent = set(train['source'].tolist() + train['target'].tolist())
    train_rel = set(train['type'].tolist())

    df = df[df['source'].isin(train_ent)]
    df = df[df['target'].isin(train_ent)]
    df = df[df['type'].isin(train_rel)]

    return df

def split(dataset, status):
    """
        Divide triples into train, valid, test sets (80%, 10%, 10%)
        #Return triples and nodes in each set
        Status for random state
    """

    df_triples = pd.read_csv(f"data/{dataset}/triples.txt", delimiter='\t', index_col=False)

    train, valid, test = np.split(df_triples.sample(frac=1, random_state=status), [int(.8*len(df_triples)), int(.9*len(df_triples))])
    valid, test = filter_set(valid, train), filter_set(test, train)
    data = triples(train, valid, test)

    data.train.to_csv(f"./data/{dataset}/train.txt", index=False, sep="\t", header=False)
    data.valid.to_csv(f"./data/{dataset}/valid.txt", index=False, sep="\t", header=False)
    data.test.to_csv(f"./data/{dataset}/test.txt", index=False, sep="\t", header=False)

    filter_triples = pd.concat([data.train, data.valid, data.test])
    filter_triples.to_csv(f"./data/{dataset}/filter_triples.txt", index=False, sep="\t", header=False)

    return triples


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parser For Arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-dataset', dest='dataset', default='lf', help='Dataset to use, default: lf')
    parser.add_argument('-seed', dest='seed', default=randint(0, 10000000), type=int, help='Random seed')

    args = parser.parse_args()

    split(dataset=args.dataset, status=args.seed)
