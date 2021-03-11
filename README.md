toronto-crime
==============================

A repo that builds a dashboard to visualize crime rates by neighbourhood in toronto while controlling for various variables (such as population and square kilometres).

Dashboard: https://toronto-crime-dash-app.herokuapp.com/
![image](https://user-images.githubusercontent.com/12496987/110340448-48cd5d00-7ff7-11eb-9116-936f9e5798e9.png)
[Glossary](https://ago-item-storage.s3.us-east-1.amazonaws.com/ca9b49e6ba7a4c319e3d203a49a76aec/MCI_Shooting_Glossary.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDwaCXVzLWVhc3QtMSJHMEUCIEHf%2B%2F5sPpwLGGasDpLnOOgd491FPA6GYKGxUVHlMPpnAiEA%2BP9j2UE7knnORHOv6wANtaCQFTt3TEUywsUE0zX5UF0qtAMIZRAAGgw2MDQ3NTgxMDI2NjUiDIO5%2F7iK70vzU6YcuCqRAzNy1ZFCFRjuf%2Fsoo2y5JFrqORU1%2BdcndsatFGsJTwBV%2FK7t5qNkzm9jzQ9ajyRtbVDDDLPy6Uzjv6T%2B5t0VD8T7fX9IppLh3wKQJZq8w5wg0P55%2B7Cy8ey%2FcXgLSFVO8F0NRDW9hGaLPf2KCZ2NkQNbWLNmflPJCFzo6LikVBYVI8R5jpmzPgcg9A25%2BWtlTkA5SqiZiZg%2F%2BJ%2B3Fz5oD0tc4bP5MM3CH4fqe3JJLyDOCjW8kESIZff4g2DOdeeQgVKpCoJacxEppWpa3evX78od9bvCxVMQG2mM4fzaSgGTR3sRncw0lrdrA09MB4xlQoFqS6Qh%2B8I4DsYoOgScYZ94GNtgafHJErnuDzOBjVB0LfvjNaZNdPDnzeWuEfxZ1kMNE3EjiZd8sEwjZaqFcDP6JN2p6ToYWxwRt1H1gNzRD6wzzkEwq8gqC8d2%2BAsQnJSTaYopVk15bKUY8aItZGTYLXH%2FuIUKZJL2rRBAss5qgzTpbAce3LZ9jeR23nhr5KuD709kIcjsYc8v%2FBrcVbR7MN6gn4IGOusBJ6Mtx6%2FxmgbUykJT8BzW4e853RRScQEV61yRUHxmtwV3Qx4JJ3nVyvcd08PNax9Tgqk7eQkvt9epCIGNm%2B4PFnE60SFVoBYttTtTMPkMKYL3s0VWegx1swFka5lMboQCCwGCXfP0ALGEflX4onlSJqXhYllfWpcp6B1EDnhm4p8TW8KFfDbAPhKkMMMYlLTtKtDm%2FwSqz%2F4hgr2CnXCHEroUJPu8gKo3ceiG9T6iTmODvISYJa9l5JyCtE0IugKgBkDc1FN2xYd9YFdE2sffpycm5wTHPrWEzz9Y7Md6Yb46YpDVVb0eiLNtuQ%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210309T201959Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAYZTTEKKEYBWOH3B2%2F20210309%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=83839fafcf1c2844e35c28974ad0476199ef29138442f5d33a63da585fbc869f) 
### Deployment
- heroku: see docs/tutorials/deploying_app_to_heroku.md
- beanstalk: docs/tutorials/deploying_app_to_beanstalk.md

### Running The Apps Locally (using 2014-2019 data):
```sh
# set your python path to the top of the repo
export PYTHONPATH="/Users/bryparker/Documents/projects/toronto/toronto-crime"
# make a virtual env and activate it (mac)
virtualenv venv
source ./venv/bin/activate
# install the requirements
pip install -r ./requirements.txt
# run the dash application:
python ./dash_app.py
# run the streamlit apps:
streamlit run ./streamlit_map_app.py 
streamlit run ./streamlit_clustering_app.py
streamlit run ./streamlit_address_app.py
```

### Running the tests:
```sh
# set your python path to the top of the repo
export PYTHONPATH="/Users/bryparker/Documents/projects/toronto/toronto-crime"
# run all tests to ensure its working properly:
python -m unittest discover ./tests/
```

### Running the data cleaning (not required unless you're updating the data)
1. download the MCI_2014_to_2019 data: https://data.torontopolice.on.ca/datasets/56a0d46ae5f141269f2598a8c07e25c1_0/data 
   - Neighbourhood_Crime_Rates_Boundary_File_.csv is already in the repo, but if you want to make it again you can see docs/tutorials/vizualizing_crime_data_for_toronto.md
2. load the csvs into sql with src/data/load_crime_data.py
3. clean the data using the scripts in ./src/data/sql
4. run src/data/make_dataset.py to save the final table to a csv

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
