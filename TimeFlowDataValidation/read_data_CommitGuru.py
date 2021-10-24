import sqlite3
import sys

"""
@return dictionary
key: a string of defect inducing commit hash
value: a list of defect fixing commit hashes
"""
def _read_fixing_commits(db_path, bootstrap_idx):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT commit_hash,fixing_commit_hash
                 FROM defect_inducing_lines_bi{0}""".format(bootstrap_idx)
    cur.execute(command)

    # for skipping the first commit for all projects
    first_commit_cregit_hash_set = set(['81cf991f580a841dd8c016921b6c567ae0c0c4f3',
                                        'cd2c32a935959baae038f7431141bbb4db1a425',
                                        '31275a67f8fa261dec38e0c5b6445d2b3d88975c',
                                        'e6a6d2bdc3e54ce5767c81ce58d3f9c80bdf500',
                                        'bf3df185d5d4149d1a4467d84e9ef71fc2e31b1'])

    defect_fixing_commits_dict = {}
    for row in cur.fetchall():
        if row[0] in first_commit_cregit_hash_set:
            continue

        if not row[0] in defect_fixing_commits_dict:
            defect_fixing_commits_dict[row[0]] = set()
        defect_fixing_commits_dict[row[0]].add(row[1])

    return defect_fixing_commits_dict

def read_fixing_commits(db_path, cregit2org_hash_dict, bootstrap_idx):
    """
    Returns:
    defect_fixing_commits: [dict<defect inducing commit hash (org), defect fixing commit hash (org)>]
    """
    temp_dict = _read_fixing_commits(db_path, bootstrap_idx)
    defect_fixing_commits = {}

    for cregit_key_hash in temp_dict.keys():

        temp_cregit_key_hash = cregit_key_hash

        if len(cregit_key_hash)!=40:
            cregit_hash_list = cregit2org_hash_dict.keys()
            for cregit_hash in cregit_hash_list:
                #if cregit_hash[:len(cregit_key_hash)]==cregit_key_hash:
                if cregit_hash[:39]==cregit_key_hash:
                    cregit_key_hash = cregit_hash
                    break   

            if len(cregit_key_hash)!=40:
                print(cregit_key_hash)
                print("cregit key error happens")
                sys.exit()


        org_key_hash = cregit2org_hash_dict[cregit_key_hash]
        defect_fixing_commits[org_key_hash] = set()

        for cregit_value_hash in temp_dict[temp_cregit_key_hash]:
            org_value_hash = cregit2org_hash_dict[cregit_value_hash]
            defect_fixing_commits[org_key_hash].add(org_value_hash)

    return defect_fixing_commits

"""
@return dictionary
key: a string of defect fixing commit hash
value: a list of defect inducing commit hashes
"""
def read_defect_inducing_commits(db_path, cregit2org_hash_dict, bootstrap_idx):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT commit_hash,defect
                 FROM defect_inducing_commits_bi{0};""".format(bootstrap_idx)
    cur.execute(command)

    defect_inducing_commits = {}
    for row in cur.fetchall():

        if not row[0] in cregit2org_hash_dict:
            continue

        defect_inducing_commits[cregit2org_hash_dict[row[0]]] = int(row[1])
        

    return defect_inducing_commits



def read_org2cregit_hash(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    #command = """SELECT org_commit_hash,view_commit_hash
    #             FROM commit_hash_pairs;"""
    command = """SELECT org_commit_hash,cregit_commit_hash
                 FROM cregit2org_commit_hashes;"""
    cur.execute(command)

    return_dict = {}
    for row in cur.fetchall():
        return_dict[row[0]] = row[1]

    return return_dict

def read_cregit2org_hash(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    command = """SELECT cregit_commit_hash,org_commit_hash
                 FROM cregit2org_commit_hashes;"""
    cur.execute(command)

    return_dict = {}
    for row in cur.fetchall():
        return_dict[row[0]] = row[1]

    return return_dict
