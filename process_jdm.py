#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import numpy as np
import collections
import dataclasses
from typing import Set, Any
import argparse
from pathlib import Path
from random import randint
from tqdm import tqdm


# pairs of symmetric relation types
JDM_SYMETRIC_RELTYPES = [(21,20), (53,54), (50,51), (41,42), (31,30), (32,115),
  (39,40), (14,26), (16,25), (3,27), (73,74), (55,56), (13,24), (6,8), (17,23),
  (15,28), (1,2000), (9,10)]


def compute_nodes_degree(df_triples):
    nodes_out_degree = collections.defaultdict(int)
    nodes_in_degree = collections.defaultdict(int)
    nodes_degree = collections.defaultdict(int)

    print('Computing node degrees:')
    for _, row in tqdm(df_triples.iterrows(), total=df_triples.shape[0]):
        nodes_out_degree[row.n1]+=1
        nodes_in_degree[row.n2]+=1
        nodes_degree[row.n1]+=1
        nodes_degree[row.n2]+=1

    return nodes_out_degree, nodes_in_degree, nodes_degree


def compute_relations_freq(df_triples):
    relation_freq = collections.defaultdict(int)

    print('Computing relation frequencies:')
    for _, row in tqdm(df_triples.iterrows(), total=df_triples.shape[0]):
        relation_freq[row.t]+=1

    return relation_freq


def get_relations_to_delete(df_triples):
    _relations_to_delete = set()

    for n, reltype_pair in enumerate(JDM_SYMETRIC_RELTYPES):
        print("Handling relation type pair: {} ({}/{})".format(reltype_pair, n+1, len(JDM_SYMETRIC_RELTYPES)))
        _edges = df_triples[df_triples["t"].isin(reltype_pair)]

        for _, _edge in _edges.iterrows():
            if _edge["t"] == reltype_pair[0]:
                other_type = reltype_pair[1]
            elif _edge["t"] == reltype_pair[1]:
                other_type = reltype_pair[0]

            symmetric_rel = _edges[(_edges["t"] == other_type) & (_edges["n1"] == _edge["n2"]) & (_edges["n2"] == _edge["n1"])]

            if symmetric_rel.shape[0] == 0:
                continue
            elif symmetric_rel.shape[0] > 1:
                print(f"Expected 0 or 1 result, got {symmetric_rel.shape[0]} instead")
                print(f"  _edge =\n{_edge}\n")
                print(f"  symmetric_rel =\n{symmetric_rel}")
                print("-" * 15)
            test = (_edge["w"] > symmetric_rel["w"]).values[0]
            _relations_to_delete.add(_edge["rid"] if test else symmetric_rel["rid"].values[0])

    print("number of relations to delete: ", len(_relations_to_delete))

    return _relations_to_delete

def convert_format(nodes, relations, triples):
    """
        Convert format to standardize ids
    """

    ent_map = dict(zip(nodes['eid'].tolist(), nodes.index.tolist()))
    rel_map = dict(zip(relations['relation_id'].tolist(), relations.index.tolist()))

    triples['type'] = triples['type'].map(rel_map)
    triples['source'] = triples['source'].map(ent_map)
    triples['target'] = triples['target'].map(ent_map)

    nodes = nodes['n']
    relations = relations['relation']

    return nodes, relations, triples


def apply_filters(df_nodes, df_relations, df_triples):
    """
        Apply filters to get subgraph
    """
    nodes_out_degree, nodes_in_degree, nodes_degree  = compute_nodes_degree(df_triples)

    # Filter 1 : Nodes connected to less than 45 other nodes (degree(node)<45) are removed.
    nodes_to_keep = [key for (key, value) in nodes_degree.items() if value >= 45]
    df_nodes16k = df_nodes[df_nodes['eid'].isin(nodes_to_keep)][["eid", "n"]].reset_index(drop=True)

    df_triples = df_triples[df_triples["n1"].isin(nodes_to_keep) & df_triples["n2"].isin(nodes_to_keep)].reset_index()

    # #Filter 2 : Relations that appeared less than 100 times in the graph are removed.
    relation_freq = compute_relations_freq(df_triples)
    relations_to_keep = [key for (key,value) in relation_freq.items() if value >= 100]
    df_triples = df_triples[df_triples["t"].isin(relations_to_keep)].reset_index()

    # # Filter 3 : For a pair of symmetric relations, the relation with the lowest weight is removed
    relations_to_delete = get_relations_to_delete(df_triples)
    df_triples = df_triples[~df_triples["rid"].isin(relations_to_delete)]

    # # Filter 2 another time
    relation_freq = compute_relations_freq(df_triples)
    relations_to_keep = [key for (key,value) in relation_freq.items() if value >= 100]
    df_triples = df_triples[df_triples["t"].isin(relations_to_keep)]

    df_triples = df_triples[["n1","t","n2"]]
    df_triples = df_triples.rename(columns={'n1': 'source', 't': 'type', 'n2': 'target'})

    nodes, relations, triples = convert_format(df_nodes16k, df_relations, df_triples)

    return nodes, relations, triples


if __name__ == '__main__':

    df_nodes = pd.read_csv("data/rezojdm16k/originals/nodes.csv", delimiter=',', index_col=False)
    df_triples = pd.read_csv("data/rezojdm16k/originals/relations.csv", delimiter=',', index_col=False)
    df_relations = pd.read_csv("data/rezojdm16k/originals/relations-ids-names.csv")

    nodes, relations, triples = apply_filters(df_nodes, df_relations, df_triples)

    nodes.to_csv('data/rezojdm16k/entities.txt', sep='\t', encoding='utf-8', index=True, header=False)
    relations.to_csv('data/rezojdm16k/relations.txt', sep='\t', encoding='utf-8', index=True, header=False)
    triples.to_csv('data/rezojdm16k/triples.txt', sep='\t', encoding='utf-8', index=False)
