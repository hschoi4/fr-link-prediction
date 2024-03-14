#!/usr/bin/env python3

import pandas as pd
import networkx as nx
import numpy as np
from sklearn.metrics import cohen_kappa_score
import seaborn as sns
import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def agreement(preds, df1, df2):
    """
        Get agreement and disagreement between two annotators
    """
    annotations = pd.merge(df1, df2, on=["Id"])
    annot_conf = pd.merge(annotations, preds, on=["Id"])     # merge with the full annotations df to get confidence score
    agree = annot_conf.loc[(annot_conf['Annotation_x'] == annot_conf['Annotation_y'])]
    disagree = annot_conf.loc[~(annot_conf['Annotation_x'] == annot_conf['Annotation_y'])]

    return agree, disagree

def kappa(df1, df2):
    """
        Get Cohen kappa between two annotators
    """
    result = pd.merge(df1, df2, on=["Id"])
    annot1 = result['Annotation_x'].tolist()
    annot2 = result['Annotation_y'].tolist()

    return cohen_kappa_score(annot1, annot2)

def get_heatmap(a1, a2, a3, a4, export):
    """
        Get heatmap with inter-annotators agreements (kappa)
    """

    data = {'A1': [40, kappa(a1, a2), kappa(a1, a3), kappa(a1, a4)],
     'A2': [kappa(a2, a1), 40, kappa(a2, a3), kappa(a2, a4)],
     'A3': [kappa(a3, a1), kappa(a3, a2), 40, kappa(a3, a4)],
     'A4': [kappa(a4, a1), kappa(a4, a2), kappa(a4, a3), 40],
     }

    heatmap_data = pd.DataFrame(data=data)
    mask = np.triu(np.ones_like(heatmap_data))

    y_axis_labels = ['A1', 'A2', 'A3', 'A4'] # labels for y-axis
    sns.set_style("dark")
    sns.heatmap(heatmap_data, yticklabels=y_axis_labels, annot=True, mask=mask, cmap="YlGnBu",vmin=0, vmax=1).set(title=f'{args.dataset}')

    if export:
        plt.savefig(f"figures/{args.dataset}_kappa.pdf")

    return plt.show()

def get_info_conf(df):
    """
        Select columns of dataframe for correlation
    """
    return df[['Annotation_x', 'Conf']]

def get_correlation(df, a1, a2, a3, a4, export):
    """
        Get figure for correlation between confidence score and manual annotations
        export: True for save figure
    """

    agree_a1_a2, disagree_a1_a2 = agreement(df, a1, a2)
    agree_a1_a3, disagree_a1_a3 = agreement(df, a1, a3)
    agree_a1_a4, disagree_a1_a4 = agreement(df, a1, a4)
    agree_a2_a3, disagree_a2_a3 = agreement(df, a2, a3)
    agree_a2_a4, disagree_a2_a4 = agreement(df, a2, a4)
    agree_a3_a4, disagree_a3_a4 = agreement(df, a3, a4)

    data_agree = pd.concat([get_info_conf(agree_a1_a2), get_info_conf(agree_a1_a3), get_info_conf(agree_a1_a4),
                            get_info_conf(agree_a2_a3), get_info_conf(agree_a2_a4), get_info_conf(agree_a3_a4)])

    sns.set_theme(style="darkgrid")
    sns.lmplot(x='Conf',y='Annotation_x',data=data_agree,fit_reg=True, height=6, scatter_kws={"s": 5}).set(title=f'{args.dataset}')
    plt.xlabel('Confidence score')
    plt.ylabel('Annotation tags')

    if export:
        plt.savefig(f"figures/{args.dataset}_correlation.pdf")
    return plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parser For Arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-dataset', dest='dataset', type=str, default="rezojdm16k", help='Dataset to use, default: rezojdm16k')
    parser.add_argument('-threshold', dest='threshold', type=int, default=0.95, help='Dataset to use, default: rezojdm16k')

    args = parser.parse_args()

    a1 = pd.read_csv(f'annotations/{args.dataset}/A1_{args.dataset}.tsv', delimiter="\t")
    a2 = pd.read_csv(f'annotations/{args.dataset}/A2_{args.dataset}.tsv', delimiter="\t")
    a3 = pd.read_csv(f'annotations/{args.dataset}/A3_{args.dataset}.tsv', delimiter="\t")
    a4 = pd.read_csv(f'annotations/{args.dataset}/A4_{args.dataset}.tsv', delimiter="\t")

    get_heatmap(a1, a2, a3, a4, False)

    if args.dataset == 'rezojdm16k':
        preds = pd.read_csv(f'predictions/{args.dataset}_all_preds.csv', delimiter="\t")
        preds['Id'] = preds.index
        df = preds.loc[(preds['Short. Path.'] >= 3)].loc[preds['Sub Nm'] != preds['Obj Nm']]

    elif args.dataset == 'rlf27k':
        preds = pd.read_csv(f'predictions/{args.dataset}_all_preds.csv', delimiter="\t")
        preds['Id'] = preds.index
        df = preds.loc[(preds['Short. Path.'] == float('inf'))].loc[preds['Sub Nm'] != preds['Obj Nm']]

    get_correlation(df, a1, a2, a3, a4, False)


    # Get triples candidates according to the threshold
    candidates = df.loc[df['Conf'] >= threshold]
    #print(candidates)
