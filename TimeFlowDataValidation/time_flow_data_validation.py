
from TimeFlowDataValidation import make_gap_parameters
from TimeFlowDataValidation import make_validation_data
from TimeFlowDataValidation import read_data_CommitGuru
from Utils import util


def separate_dict(db_path, author_date_pickle_path, dict_data, start_day, gap_days, bootstrap_idx, unit_days=30):

    """
    Extract author_date of the commits that change at least one soure code line.
    """
    author_date = util.load_pickle(author_date_pickle_path)

    start_gap_days, end_gap_days, gap_days, unit_days, training_period = make_gap_parameters.make_gap_parameters(author_date, start_day, gap_days, unit_days=unit_days)

    """
    Make an instance that manage start and end time of training, gap and test data
    """
    #time_keeper = make_validation_data.TimeManeger(author_date,0,0)
    time_keeper = make_validation_data.TimeManeger(author_date, start_gap_days=start_gap_days, end_gap_days=end_gap_days, gap_days=gap_days, unit_days=unit_days, training_period=training_period)

    """
    The author_date is used to decide training, gap and test commits with
    the TimeManeger instance.
    """
    training_commits, gap_commits, test_commits, others = time_keeper.validation_commit(author_date)

    """
    Extract defect_fixing_commits. The key is defect inducing commit.
    The value is a list of defect fixing commit(s) corresponding to the key.
    """
    cregit2org_hash_dict = read_data_CommitGuru.read_cregit2org_hash(db_path)
    defect_fixing_commits = read_data_CommitGuru.read_fixing_commits(db_path, cregit2org_hash_dict, bootstrap_idx)

    """
    Make a dictionary of labels of defective commits. The key is the commit that
    changes at least one source code line. The value is a binary: 0 refers to
    clean and 1 refers to defective.
    When we label each commit, we use all commits.
    In addition, we do the same procedure for the training commits.
    However, then we only use training commits and gap commits to label
    the training commits not all commits.
    """
    all_label_dict = make_validation_data.decide_defect_label_all_data(db_path, bootstrap_idx) # using source code change commits to label
    training_label_dict = make_validation_data.decide_defect_label_training_data(defect_fixing_commits, training_commits, gap_commits)

    # for key error, we use ast type function
    train_data, train_label, test_data, test_label = make_validation_data.make_validation_data(training_commits, test_commits, training_label_dict, all_label_dict, dict_data)

    return train_data, train_label, test_data, test_label, time_keeper, author_date, defect_fixing_commits, training_period, test_commits



def separate_dict_update(db_path, time_keeper, author_date, defect_fixing_commits, dict_data, bootstrap_idx):

    time_keeper.time_update()

    """
    The author_date is used to decide training, gap and test commits with
    the TimeManeger instance.
    """
    training_commits, gap_commits, test_commits, others = time_keeper.validation_commit(author_date)

    """
    Make a dictionary of labels of defective commits. The key is the commit that
    changes at least one source code line. The value is a binary: 0 refers to
    clean and 1 refers to defective.
    When we label each commit, we use all commits.
    In addition, we do the same procedure for the training commits.
    However, then we only use training commits and gap commits to label
    the training commits not all commits.
    """
    all_label_dict = make_validation_data.decide_defect_label_all_data(db_path, bootstrap_idx) # using source code change commits to label
    training_label_dict = make_validation_data.decide_defect_label_training_data(defect_fixing_commits, training_commits, gap_commits)


    train_data, train_label, test_data, test_label = make_validation_data.make_validation_data(training_commits, test_commits, training_label_dict, all_label_dict, dict_data)


    return train_data, train_label, test_data, test_label, test_commits

