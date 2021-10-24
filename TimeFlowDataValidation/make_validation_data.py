import datetime
from TimeFlowDataValidation import read_data_CommitGuru


class TimeManeger():
    def __init__(self, author_date, start_gap_days=0, end_gap_days=0, gap_days=200, unit_days=100, training_period=3):

        self.START = min(author_date.values()) + datetime.timedelta(days=start_gap_days) # date (date + delta)
        self.END = max(author_date.values()) - datetime.timedelta(days=end_gap_days) # date ( date - delta)
        self.GAP = datetime.timedelta(days=gap_days) # delta
        self.UNIT = datetime.timedelta(days=unit_days) # delta
        self.training_period = training_period

        self.training_times_start = self.START # date
        self.training_times_end = self.training_times_start + self.training_period*self.UNIT # date (date + delta)
        self.gap_times_end = self.training_times_end + self.GAP # date (date + delta)
        self.test_times_end = self.gap_times_end + self.UNIT # date (date + delta)

    def disp(self):

        print('START: {0}'.format(self.START))
        print('END: {0}'.format(self.END))
        print('GAP: {0}'.format(self.GAP))
        print('UNIT: {0}'.format(self.UNIT))
        print('Training period: {0}'.format(self.training_period))
        print('Training days: {0}'.format(self.UNIT*self.training_period))

        print('training_times_start: {0}'.format(self.training_times_start))
        print('training_times_end: {0}'.format(self.training_times_end))
        print('gap_times: {0}'.format(self.gap_times_end))
        print('test_times: {0}'.format(self.test_times_end))
        #print(hashes)

        print('The actual end gaps: {0}'.format((self.END - self.test_times_end) + datetime.timedelta(days=365)))
    
    def return_basic_info(self):
        return {'eng_gap': (self.END - self.test_times_end) + datetime.timedelta(days=365),
                'gap': self.GAP,
                'unit': self.UNIT,
                'training_interval': self.UNIT*self.training_period,
                'iteration_step_size': self.training_period}


    def time_update(self):
        self.training_times_start = self.training_times_start + self.UNIT # date
        self.training_times_end = self.training_times_start + self.training_period*self.UNIT # date
        self.gap_times_end = self.training_times_end + self.GAP # date
        self.test_times_end = self.gap_times_end + self.UNIT # date

    def validation_commit(self, author_date):

        training_commits = []
        gap_commits = []
        test_commits = []
        others = []

        for commit_hash in author_date.keys():

            if self.training_times_start <= author_date[commit_hash] and author_date[commit_hash] < self.training_times_end:
                training_commits.append(commit_hash)
            elif self.training_times_end <= author_date[commit_hash] and author_date[commit_hash] < self.gap_times_end:
                gap_commits.append(commit_hash)
            elif self.gap_times_end <= author_date[commit_hash] and author_date[commit_hash] < self.test_times_end:
                test_commits.append(commit_hash)
            else:
                others.append(commit_hash)
                #pass

        return training_commits, gap_commits, test_commits, others


def decide_defect_label_training_data(defect_fixing_commits, training_commits, gap_commits):

    hashes = list(training_commits)
    hashes.extend(gap_commits)
    #print(len(training_commits))
    #print(len(gap_commits))
    #print(len(hashes))
    hashes = set(hashes)

    defect = {}

    for commit_hash in training_commits: # Make label for only training data (commits)

        defect[commit_hash]=0 # Initially add 0 equals to not defect inducing commit

        if not commit_hash in defect_fixing_commits:
            continue
        
        for fixing_commit_hash in defect_fixing_commits[commit_hash]: # Analyze each defect fixing commit on the commit if the commit has them.

            """
            If commit_hash in training data has defect fixing commit (fixing_commit_hash) and the fixing_commit_hash
            is contained in either training data or gap data, we label the commit_hash as a defective commit.
            """
            if fixing_commit_hash in hashes:
                defect[commit_hash] = 1
                break

    #print(sum(defect.values())/len(defect.values()))
    #print(defect)
    return defect

def decide_defect_label_all_data(db_path, bootstrap_idx):

    cregit2org_hash_dict = read_data_CommitGuru.read_cregit2org_hash(db_path)
    defect = read_data_CommitGuru.read_defect_inducing_commits(db_path, cregit2org_hash_dict, bootstrap_idx)

    return defect

def make_validation_data(training_commits, test_commits, training_label_dict, all_label_dict, change_metrics_dict):

    training_data = []
    training_label = []
    test_data = []
    test_label = []

    for commit_hash in training_commits:

        if not commit_hash in training_label_dict:
            continue

        try:
            training_data.append(change_metrics_dict[commit_hash])
            training_label.append(training_label_dict[commit_hash])
        except KeyError:
            print('Key error happend. The commit is:')
            print(commit_hash)
            assert len(training_data)==len(training_label), "Different length in make_validation_data_AST in training"

    for commit_hash in test_commits:

        if not commit_hash in all_label_dict:
            continue

        try:
            test_data.append(change_metrics_dict[commit_hash])
            test_label.append(all_label_dict[commit_hash])
        except KeyError:
            print('Key error happend. The commit is:')
            print(commit_hash)
            assert len(test_data)==len(test_label), "Different length in make_validation_data_AST in test"


    return training_data, training_label, test_data, test_label

