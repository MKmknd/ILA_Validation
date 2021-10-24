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
