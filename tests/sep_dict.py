import datetime
import sqlite3
import sys
import csv

from TimeFlowDataValidation import time_flow_data_validation
from TimeFlowDataValidation import initializer
from Utils import util

project_name_list = ['avro']
ila_list=["1"]
delete_rate_list = ["0"]

modelName = ['LR']

repo_path = "./../../../repository/{0}"
bootstrap_idx = 0

START_GAP = 30

def read_change_metrics_context(db_path):
    """Extract snippet data from database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT commit_hash,fix,ns,nd,nf,entrophy,la,ld,lt,ndev,age,nuc,exp,rexp,sexp
                 FROM data
                 ORDER BY id;"""
    cur.execute(command)

    metrics = {}
    for row in cur.fetchall():
        temp_change_metrics = []
        for cnt, value in enumerate(row[1:]):
            try:
                temp_change_metrics.append(float(value))
            except ValueError:
                if value=='False':
                    temp_change_metrics.append(0)
                elif value=='True':
                    temp_change_metrics.append(1)
                elif cnt == 0:
                    temp_change_metrics.append(0)
                else:
                    sys.exit()
        metrics[row[0]] = temp_change_metrics

    conn.close()

    return metrics

def extract_change_metrics(p_name):

    change_metrics = read_change_metrics_context("./commitguru_data/{0}.db".format(p_name))
    return change_metrics



def initialize_authordate():
    initializer.authordate_initialize(repo_path, project_name_list)

def read_csv(csv_path):
    data = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(list(map(int, row)))

    return data

def main():

    initialize_authordate()
    initializer.merge_commit(project_name_list, repo_path)

    answer_data = read_csv("./answer/label_avro_LR_1.csv")

    for delete_rate in delete_rate_list:

        for ILA_num in ila_list:

            for p_name in project_name_list:


                db_path = "./data/{0}_{1}_delete{2}.db".format(p_name, ILA_num, delete_rate) # cv fold

                author_date_pickle_path = "./data/gap_para_author_date_{0}_without_merge.pickle".format(p_name)

                merge_commits = util.load_pickle("./data/{0}_merge.pickle".format(p_name))
                first_author_date, median_defect_fixing_interval = \
                    initializer.return_initial_parameters(db_path, p_name, author_date_pickle_path, bootstrap_idx, merge_commits)

                # read metrics (dict<commit hash, metrics>)
                change_metrics_dict = extract_change_metrics(p_name)

                first_author_date = first_author_date + datetime.timedelta(days=START_GAP)
                start_day = datetime.datetime(year=first_author_date.year,month=first_author_date.month,day=first_author_date.day)
                median_defect_fixing_interval = datetime.timedelta(days=median_defect_fixing_interval)

                train_data, train_label, test_data, test_label, time_keeper, \
                author_date, defect_fixing_commits, training_period, test_commits \
                    = time_flow_data_validation.separate_dict(db_path, author_date_pickle_path, change_metrics_dict,
                                                              start_day, median_defect_fixing_interval, bootstrap_idx=bootstrap_idx)

                minus_cnt = 0
                for ite in range(training_period):
                #for ite in range(2):

                    #if len(train_label)==0 or sum(train_label)==0 or len(test_label)==0 or sum(test_label)==0:
                    if len(test_label)==0:
                        # updating training data.
                        train_data, train_label, test_data, test_label, test_commits \
                            = time_flow_data_validation.separate_dict_update(db_path, time_keeper,
                                                                             author_date, defect_fixing_commits,
                                                                             change_metrics_dict, bootstrap_idx)
                        minus_cnt += 1
                        continue

                    """
                    ===================================================
                    ===================================================
                    your prediction script should be here
                    ===================================================
                    ===================================================
                    """


                    assert len(test_label)==len(answer_data[ite-minus_cnt]), \
                        "diff length: ans - {0} and target - {1}".format(len(answer_data[ite-minus_cnt]),
                                                                         len(test_label))

                    assert test_label==answer_data[ite-minus_cnt], \
                        "diff content: ite - {0}".format(ite)

                    tmp_dict = time_keeper.return_basic_info()
                    if (tmp_dict['iteration_step_size']-1)==ite:
                        for para_name in ['eng_gap', 'gap', 'unit', 'training_interval', 'iteration_step_size']:
                            print("{0}: {1}".format(para_name, tmp_dict[para_name]))

                    # updating training data.
                    train_data, train_label, test_data, test_label, test_commits \
                        = time_flow_data_validation.separate_dict_update(db_path, time_keeper,
                                                                         author_date, defect_fixing_commits,
                                                                         change_metrics_dict, bootstrap_idx)

    print("TEST DONE")

if __name__=="__main__":

    main()
