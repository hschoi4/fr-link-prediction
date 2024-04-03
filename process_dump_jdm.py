#!/usr/bin/env python3

import sys
import os
import pyspark as ps
import warnings
import re
import datetime
import collections

from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import Row
from pyspark.sql.types import StringType


JDM_MAX_WEIGHT = 50
JDM_BLACK_LIST_RELATIONS_ID = [12, 18, 29, 33, 36, 45, 46, 47, 48, 1000, 1001, 1002, 444, 128, 200]
JDM_TYPE_1 = 1
JDM_TYPE_2 = 2

def init_jdm_nodes_and_relations():
    """
        Get dump and filter nodes and relations
    """
    sc = SparkSession.Builder().appName("RezoJDM-SDS").getOrCreate().sparkContext
    jdmDUMP = sc.textFile("data/rezojdm16k/originals/09032019-LEXICALNET-JEUXDEMOTS-FR-NOHTML.txt")

    jdmNodes = jdmDUMP.filter(lambda x: x[:4] == "eid=")
    jdmNodes = jdmNodes.map(lambda x:
                            Row(eid = int(re.findall("eid=(\d+)\|n=", x)[0]),
                                n = re.findall("n=\"(.+)\"\|t=", x)[0],
                                t = int(re.findall("t=(-?\d+)\|w=", x)[0]),
                                w = int(re.findall("w=(-?\d+)", x)[0])))

    # only type 1 and 2 are kept
    jdmNodes = jdmNodes.filter(lambda x: (x["t"] == JDM_TYPE_1) | (x["t"] == JDM_TYPE_2))

    # node whose text starts and ends with equal (“=”) are not french, don’t keep them
    jdmNodes = jdmNodes.filter(lambda x: ( ~((x["n"][0] == "=") & (x["n"][-1] == "="))))

    # filter the weights lesser than M(>50)
    jdmNodes = jdmNodes.filter(lambda x: x["w"] > JDM_MAX_WEIGHT)

    dfNodes = jdmNodes.toDF()

    jdmRelations = jdmDUMP.filter(lambda x: x[:4] == "rid=")
    jdmRelations = jdmRelations.map(lambda x:
                                        Row(rid = int(re.findall("rid=(\d+)\|n1=", x)[0]),
                                            n1 = int(re.findall("n1=(\d+)\|n2=", x)[0]),
                                            n2 = int(re.findall("n2=(-?\d+)\|t=", x)[0]),
                                            t = int(re.findall("t=(-?\d+)\|w=", x)[0]),
                                            w = int(re.findall("w=(-?\d+)", x)[0])))

    # only relations with weight > 50 are kept
    jdmRelations = jdmRelations.filter(lambda x: x["w"] > JDM_MAX_WEIGHT)

    # keep all nodes except those in JDM_BLACK_LIST_RELATIONS_ID
    jdmRelations = jdmRelations.filter(lambda x: x["t"] not in JDM_BLACK_LIST_RELATIONS_ID)

    # edges might refer to non-existing node, don’t keep those edges
    existing_node_ids = list(dfNodes.toPandas()["eid"])
    jdmRelations = jdmRelations.filter(lambda x: (x["n1"] in existing_node_ids) & (x["n2"] in existing_node_ids))

    # convert to pandas
    jdmNodes = jdmNodes.toDF().toPandas()
    jdmRelations = jdmRelations.toDF().toPandas()

    return jdmNodes, jdmRelations


if __name__ == '__main__':

    dfNodes, dfRelation = init_jdm_nodes_and_relations()
    dfNodes.to_csv("data/rezojdm16k/originals/nodes.csv", index=False)
    dfRelations.to_csv("data/rezojdm16k/originals/relations.csv", index=False)
