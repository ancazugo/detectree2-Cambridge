# Improving Urban Tree Management Using High-Resolution Satellite Data

This repository contains all the code related to Andrés Camilo Zúñiga González’s Master Thesis titled *Improving Urban Tree Management Using High-Resolution Satellite Data*, as part of the AI4ER CDT at the University of Cambridge.

## Code

The core code, which was used in Google Colab Pro to develop and obtain the results presented in the final report, is contained in the following notebooks:

1. [Data Preprocessing](preprocessing.ipynb): Data pre-processing of the aerial images and manually labelled crowns.
2. [Model Training](training.ipynb): Training with wandb and hyperparameter tuning for all configurations of the model.
3. [Prediction](prediction.ipynb): Predictions for the best model in each configuration of the best models.
## Weights & Biases Report

The report for all the model runs is available in the [W&B project report](https://wandb.ai/ancazugo/detectree2-Cambridge/).

## Data

The data used in this project is available thorugh [Zenodo](https://zenodo.org/record/8099445).

## Interactive Results

Finally, a city-wide interactivce map of the predictions can be found in this repository’s [main page](ancazugo.github.io/detectree2-Cambridge/).
