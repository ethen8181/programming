# Kaggle Don't Get Kicked

Predict if a car purchased at auction is a unfortunate purchase. Problem description is available at https://www.kaggle.com/c/DontGetKicked

## Installation

This assumes the user already has Anaconda installed and is targeted for Python3.6

```bash
pip install -r requirements.txt
```

## Usage

```bash
# assuming we're at the project's root directory

# train the model on the training set and store it
python src/main.py --train --inputfile training.csv --outputfile prediction.csv

# predict on future dataset and output the prediction
# to a .csv file in a output directory (will be created
# one level above where the script is if it doesn't exist yet)
python src/main.py --inputfile test.csv --outputfile prediction_future.csv
```

## Documentation

- `src/main.ipynb` Jupyter Notebook that contains a walkthrough of the overall process. This is the best place to start. [[nbviewer](http://nbviewer.jupyter.org/github/ethen8181/machine-learning/blob/master/projects/kaggle_dont_get_kicked/src/main.ipynb)][[html](http://ethen8181.github.io/machine-learning/projects/kaggle_dont_get_kicked/src/main.html)]
- `src/main.py` Upon walking through the notebook to familiarize ourself with the process, we can just run this Python script to run the end to end pipeline. [[Python script](https://github.com/ethen8181/machine-learning/blob/master/projects/kaggle_dont_get_kicked/src/main.py)]
- `src/utils.py` Utility function for the project used throughout the Jupyter notebook and Python script. [[Python script](https://github.com/ethen8181/machine-learning/blob/master/projects/kaggle_dont_get_kicked/src/utils.py)]
