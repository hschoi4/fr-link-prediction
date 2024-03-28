#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import numpy as np
import collections
import dataclasses
from typing import Set, Any
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

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

def get_files():

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

    print('Create all triples file')
    ent_map = dict(zip(entities['id'].tolist(), entities['label'].tolist()))
    rel_map = dict(zip(relations['id'].tolist(), relations['name'].tolist()))

    triples['type'] = triples['type'].map(rel_map)
    triples['source'] = triples['source'].map(ent_map)
    triples['target'] = triples['target'].map(ent_map)

    triples.to_csv(pathdir / 'triples.txt', index=False, sep="\t")

    return triples


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parser For Arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-data', dest='dataset', default='lf', help='Dataset to use, default: lf')
    parser.add_argument('-seed', dest='seed', default=randint(0, 10000000), type=int, help='Random seed')

    args = parser.parse_args()

    # triples
    triples = get_files()
