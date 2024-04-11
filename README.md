# French Link Prediction

This repository contains the code necessary to reproduce results of the LREC-COLING 2024 paper, **Beyond Model Performance: Can Link Prediction Enrich French Lexical Graphs?**.

We use the models from Mirzapour et al. 2022 within the framework OpenKE and their subgraph of JeuxDeMots, RezodJDM16k. We also use a CompGCN model from Vashishth et al. 2020.

## Installation

- CUDA version: 12.1
- Pytorch: 2.2.0
- python = 3.10

Get the right version for pytorch and cuda here: https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html

```
conda create -n fr-lp python=3.10
pip install torch_geometric ordered_set carbontracker wandb my-torch tabulate
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.2.0+cu121.html
pip install torch==2.2
```

## Download and process lexical resources

`download_data.sh <rlf or jdm>`

Get the originals files:
- RL-fr version 2.1
- JeuxDeMots dump of 09/03/2019

### JeuxDeMots and RezoJDM16k

Script `process_dump_jdm.py` applies filters to obtain a intermediate subgraph of JeuxDeMots. The code comes from the original one in Mirzapour et al. 2022 but does not compile. The intermediate subgraph is available and can be used to obtain the final graph, RezoJDM16k, with the following commands:

```
cp french-kg/resources/datasets/Filtered_Nodes_Edges/nodes.csv french-kg/resources/datasets/Filtered_Nodes_Edges/relations.csv data/rezojdm16k/originals/.
cp french-kg/resources/datasets/Triplets/relations_ids_names.csv data/rezojdm16k/originals/relations-ids-names.csv
```

Get the data in right format with `process_jdm.py`.

### RL-fr

RL-fr represents senses of a word into different nodes linked by copolysemy relations (cp). Syntagmatic and paradigmatic relations are represented through lexical functions (lf), which can be complex (689 different lexical functions in RL-fr v2). We can group the lexical functions according to their families (lffam).

`python3 process_rlf.py -dataset lffam-cp`
* lffam : relations as lexical function families
* lf : relations as lexical functions
* lffam-cp : lexical function families and copolysemy relations
* lf-cp : lexical function and copolysemy relations

### Division train, valid, test sets

`python3 split.py -dataset <rezojdm16k or rlf/lffam-cp> -seed <int>`

## Training models

### OpenKE models

Run the following commands:
```bash
cd french-kg/trainrs/OpenKE/
mkdir checkpoint
mkdir result
cd openke
bash make.sh
```

Convert into openKE format and run the models. (Do not forget to change the path in `run_models.py` to access OpenKE trainers.)

```python3
python3 french-kg/openKE.py -dataset <dataset_name>
python3 french-kg/n-n.py -dataset <dataset_name>
python3 french-kg/run_models.py -dataset <dataset_name>
```

### CompGCN model

`python3 CompGCN/run.py -data <dataset name>`

## Confidence-aware predictions

Generate torch files containing predictions with a confidence score using a MC Dropout algorithm. Create `checkpoints` folder and put the checkpoint of the model used. Requires a lot of memory.

`mc_dropout.py -dataset <dataset name> -checkpoint <checkpoint> -save-every <int>`

## Results analysis

Process the predictions `predictions.py`. Final predictions used in our experiments are available here:
```
wget https://pimo.id/e4fc01f0/predictions.zip
unzip predictions.zip
```

Make annotation batches `annotations.py`

Get the results (process annotations, make figures and get candidates according to a threshold): `results.py -dataset <dataset name>`
