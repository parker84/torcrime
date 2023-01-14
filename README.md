TorCrime
==============================

A repo that builds a dashboard investigate crime in your neighbourhood.
https://torcrime.herokuapp.com/

<img width="1702" alt="image" src="https://user-images.githubusercontent.com/12496987/212494778-2011f84f-94ea-4870-9a37-8cca83d06bb1.png">

<img width="1629" alt="image" src="https://user-images.githubusercontent.com/12496987/212494815-75574f2e-f11d-409a-978b-5ff01d2f10fc.png">



### Deployment
- heroku: see docs/tutorials/deploying_app_to_heroku.md
- beanstalk: docs/tutorials/deploying_app_to_beanstalk.md

### Running The Apps Locally (using 2014-2019 data):
```sh
# set your python path to the top of the repo
export PYTHONPATH="/Users/brydonparker/Documents/Projects/side_projects/torcrime"
# make a virtual env and activate it (mac)
virtualenv venv
source ./venv/bin/activate
# install the requirements
./venv/bin/python -m pip install -r ./requirements.txt
# run the streamlit app:
./venv/bin/python -m streamlit run ./app.py
# running the crime app
python3 ./alert_app.py
```

### Running the tests:
```sh
# set your python path to the top of the repo
export PYTHONPATH="/Users/brydonparker/Documents/Projects/side_projects/torcrime"
# run all tests to ensure its working properly:
python3 -m unittest discover ./tests/
# running all pytests (for the tweet system)
python3 -m pytest ./tests/pytests/ --capture=no # Note: if you want to use a debugger (like ipdb) add --capture=no to the end of this
```

### Running the data cleaning (not required unless you're updating the data)
1. download the MCI_2014_to_2019 data: https://data.torontopolice.on.ca/datasets/56a0d46ae5f141269f2598a8c07e25c1_0/data 
   - Neighbourhood_Crime_Rates_Boundary_File_.csv is already in the repo, but if you want to make it again you can see docs/tutorials/vizualizing_crime_data_for_toronto.md
2. load the csvs into sql with src/data/load_crime_data.py
3. clean the data using the scripts in ./src/data/sql
4. run src/data/make_dataset.py to save the final table to a csv

### Getting db ready
```sh
# scrape all the recent tweets into the db
python3 ./src/data/tweet_scrapper.py 
```

### Deployment Documentation
- Deployment see here: /docs/tutorials/deploying_app_to_beanstalk.md


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
