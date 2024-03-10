#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import collections
import dataclasses
from typing import Set, Any
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
from random import randint

@dataclasses.dataclass
class triples:
    train: Any
    valid: Any
    test: Any

@dataclasses.dataclass
class Nodes:
    train: Set = dataclasses.field(default_factory=set)
    valid: Set = dataclasses.field(default_factory=set)
    test: Set = dataclasses.field(default_factory=set)
    intersection : Set = dataclasses.field(default_factory=set)

def get_entities(df_nodes):
    """
        Get label of each node and new ids
    """
    entities = df_nodes['lexname'].tolist()
    list_labels = []

    # Get the label and features between tags in xml format
    for ent in entities:
        tag = ET.fromstring('<tag>'+ent+"</tag>")
        acc = ""
        for field in tag:
            acc = acc + " " + field.text
        list_labels.append(acc.strip())

    df_nodes['label'] = list_labels

    return df_nodes

def get_lf_families():
    """
    Returns dictionary with lf family and its corresponding lf
    """

    dic = {}
    tree = ET.parse("data/rlf/originals/14-lslf-model.xml")
    root = tree.getroot()
    for child in root:
        for gc in child:
            dic[gc.attrib['id']] = [ggc.attrib['id'] for ggc in gc]
    return dic

def get_default_format(df, entities, relations):
    """
        Put labels for relations and entities
    """
    ent_map = dict(zip(entities['id'].tolist(), entities['label'].tolist()))
    rel_map = dict(zip(relations['id'].tolist(), relations['name'].tolist()))

    df['type'] = df['type'].map(rel_map)
    df['source'] = df['source'].map(ent_map)
    df['target'] = df['target'].map(ent_map)

    #df = df.drop(columns='id')

    return df

def filter_set(df, train):
    train_ent = set(train['source'].tolist() + train['target'].tolist())
    train_rel = set(train['type'].tolist())

    df = df[df['source'].isin(train_ent)]
    df = df[df['target'].isin(train_ent)]
    df = df[df['type'].isin(train_rel)]

    return df

def split(df_triples, status):
    """
        Divide triples into train, valid, test sets (80%, 10%, 10%)
        #Return triples and nodes in each set
        Status for random state
    """
    train, valid, test = np.split(df_triples.sample(frac=1, random_state=status), [int(.8*len(df_triples)), int(.9*len(df_triples))])
    valid, test = filter_set(valid, train), filter_set(test, train)
    triples = triples(train, valid, test)

    # nodes = Nodes()
    # nodes.train = set(train["source"]).union(set(train["target"]))
    # nodes.valid = set(valid["source"]).union(set(valid["target"]))
    # nodes.test = set(test["source"]).union(set(test["target"]))
    # nodes.intersection =  nodes.train.intersection(nodes.valid).intersection(nodes.test)

    return triples

def get_triples():

    #nodes
    nodes = pd.read_csv("data/rlf/originals/01-lsnodes.csv", sep="\t")
    entities = get_entities(nodes)

    # relations
    lf = pd.read_csv("data/rlf/originals/lf-ids-names.csv", sep="\t")
    lffam = pd.read_csv("data/rlf/originals/lffam-ids-names.csv", sep="\t")
    cp = pd.read_csv("data/rlf/originals/cp-ids-names.csv", sep="\t")

    # triples
    df_lf = pd.read_csv("data/rlf/originals/15-lslf-rel.csv", sep="\t")
    df_lf = df_lf[['source', 'lf', 'target']]
    df_lf.columns = df_lf.columns.str.replace("lf", "type")

    df_cp = pd.read_csv("data/rlf/originals/04-lscopolysemy-rel.csv", sep="\t")
    df_cp = df_cp[['source', 'type', 'target']]

    if args.dataset == 'lf':
        triples = df_lf
        relations = lf

    elif args.dataset == 'lf-cp':
        triples = pd.concat([df_lf, df_cp], ignore_index=True)
        relations = pd.concat([lf, cp], ignore_index=True)

    elif args.dataset == 'lffam':
        lf_fam = get_lf_families()
        triples = df_lf.copy()
        for fam, lf in lf_fam.items():
            triples['type'] = triples['type'].replace(lf, fam)

        relations = lffam

    elif args.dataset == 'lffam-cp':
        lf_fam = get_lf_families()
        df_lffam = df_lf.copy()
        for fam, lf in lf_fam.items():
            df_lffam['type'] = df_lffam['type'].replace(lf, fam)

        triples = pd.concat([df_lffam, df_cp], ignore_index=True)
        relations = pd.concat([lffam, cp], ignore_index=True)

    pathdir = Path('./data/rlf') / Path(args.dataset).name
    pathdir.mkdir(parents=True, exist_ok=True)

    print('Create entities and relations files')
    entities['label'].to_csv(pathdir / 'entities.txt', index=True, sep="\t", header=False)
    relations['name'].to_csv(pathdir / 'relations.txt', index=True, sep="\t", header=False)

    print('Create all triplets file')
    triples = get_default_format(triples, entities, relations)
    triples.to_csv(pathdir / 'triples.txt', index=False, sep="\t")

    print('Divide into train, validation, test sets and apply filters on validation and test sets')
    data = split(triples, args.seed)
    data.train.to_csv(pathdir / 'train.txt', index=False, sep="\t", header=False)
    data.valid.to_csv(pathdir / 'valid.txt', index=False, sep="\t", header=False)
    data.test.to_csv(pathdir / 'test.txt', index=False, sep="\t", header=False)

    print('Create all triplets files without those removed')
    filter_triples = pd.concat([data.train, data.valid, data.test])
    filter_triples.to_csv(pathdir / 'filter_triples.txt', index=False, sep="\t", header=False)


    return triples


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parser For Arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-data', dest='dataset', default='lf', help='Dataset to use, default: lf')
    parser.add_argument('-seed', dest='seed', default=randint(0, 10000000), type=int, help='Random seed')

    args = parser.parse_args()

    # triples
    triples = get_triples()
