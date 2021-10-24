
## Abstract
This library can be used to implement a defect prediction model for an ILA,
studied projects, and a dataset scenario in our paper. 
This library corresponds to the validation scheme (online change classification)
that we described in Section 5.8. 
You need to prepare a prediction model, a resampling technique, a preprocessing
technique, and a hyper-parameter optimization technique.  

## How to install

In your Python environment, please conduct the following:

```
$ cd {{path to the root directory of this repository}}
$ pip install -e .
```

If you use pipenv,

```
$ cd {{path to the root directory of this repository}}
$ pipenv sync
```


## How to prepare the database
Users first need to prepare a database in which
defect-inducing commits information, the pair between defect-inducing commit and defect-fixing commit,
and (if you use,) the pair between cregit commit hashes and
original commit hashes are stored. 

Below I briefly explain the database schema and examples.
Here, we need at least four tables:

- defect_inducing_lines_bi{{*}}(commit_hash, fixing_commit_hash)
- defect_inducing_commits_bi{{*}}(commit_hash, defect)
- defect_fixing_commits_bi{{*}}(commit_hash)
- cregit2org_commit_hashes(cregit_commit_hash, org_commit_hash)

Note that {{*}} refers to a number to representa a repetition in the paper.

If you use cregit to extract defect-inducing commits and lines data,
please make sure all commit hashes are cregit commit hashes except for
org_commit_hash in the database.
If you use the original repository instead, please make sure
all commit hashes are the original commit hashes even though
the column is cregit_commit_hash.

### defect_inducing_lines_bi{{*}}
This table includes all pairs between defect-inducing commits (commit_hash column)
and defect-fixing commits (fixing_commit_hash column).

### defect_inducing_commits_bi{{*}}
This table includes all commit hashes (commit_hash column) and
the defective commit information (defect).
The defective commit information is 0 (clean commits) or 1 (defective commits).

### defect_fixing_commits_bi{{*}}
This table includes all defect-fixing commit hashes.

### cregit2org_commit_hashes
This table includes all pairs between the cregit commit hashes and
the original commit hashes.


## How to get the result
Please check the main function in the following script:
- tests/sep_dict.py

### 1. Prepare the directory

```
$ cd {{path to the working directory}}
$ mkdir data
```

### 2. Prepare the arguments
Users need to prepare the following arguments:
- project_name_list: list of studied projects
- db_path: path to the database that was created in the above process
- repo_path: path to the original repository of the studied projects (project name should be replaced with "{0}"
- data_dict_path: path to a pickle file: dictionary<commit hash, list<features>> a dictionary of a metrics set for all the commits. The key is an original commit hash; the value is a list of metrics of this commit.
- bootstrap_idx: This is a number for the tables in the database.
- START_GAP: start gap days

### 3. Execute the script

I show the smallest script:

```Python

from TimeFlowDataValidation import time_flow_data_validation
from TimeFlowDataValidation import initializer
import datetime
from Utils import util

project_name_list = ['project_name']
db_path = "./db/{0}_database.db" # {0} corresponds to project name
repo_path = "./repository/{0}" # {0} corresponds to project name
data_dict_path = "./data/{0}_metrics.pickle"
bootstrap_idx = 0
START_GAP = 30


initializer.authordate_initialize(repo_path, project_name_list)
initializer.merge_commit(project_name_list, repo_path)

for p_name in project_name_list:


    author_date_pickle_path = "./data/gap_para_author_date_{0}_without_merge.pickle"
    merge_commits = util.load_pickle("./data/{0}_merge.pickle".format(p_name))
    first_author_date, median_defect_fixing_interval = \
        initializer.return_initial_parameters(db_path.format(p_name), p_name, author_date_pickle_path.format(p_name), bootstrap_idx, merge_commits)

    first_author_date = first_author_date + datetime.timedelta(days=START_GAP)
    start_day = datetime.datetime(year=first_author_date.year,month=first_author_date.month,day=first_author_date.day)
    median_defect_fixing_interval = datetime.timedelta(days=median_defect_fixing_interval)

    data_dict = util.load_pickle(data_dict_path.format(p_name))

    train_data, train_label, test_data, test_label, time_keeper, \
    author_date, defect_fixing_commits, training_period, test_commits \
        = time_flow_data_validation.separate_dict(db_path.format(p_name), author_date_pickle_path.format(p_name), data_dict,
                                                    start_day, median_defect_fixing_interval, bootstrap_idx=bootstrap_idx)

    # repeat the prediction for all the iterations (training_period = # of iterations)
    for ite in range(training_period):

        # if test data is empty, skip this iteration
        if len(test_label)==0:
            # updating training data.
            train_data, train_label, test_data, test_label, test_commits \
                = time_flow_data_validation.separate_dict_update(db_path.format(p_name), time_keeper,
                                                                    author_date, defect_fixing_commits,
                                                                    data_dict, bootstrap_idx)
            continue

        """
        ===================================================
        ===================================================
        your prediction script should be here
        ===================================================
        ===================================================
        """


        # updating training data.
        train_data, train_label, test_data, test_label, test_commits \
            = time_flow_data_validation.separate_dict_update(db_path.format(p_name), time_keeper,
                                                                author_date, defect_fixing_commits,
                                                                data_dict, bootstrap_idx)


```




