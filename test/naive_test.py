#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import traceback

from utils import check_experiment_status, fetch_experiment_config, read_last_line, remove_files, setup_experiment

GREEN = '\33[32m'
RED = '\33[31m'
CLEAR = '\33[0m'

EXPERIMENT_URL = 'http://localhost:8080/api/v1/nni/experiment'

def run(installed = True):
    
    to_remove = ['tuner_search_space.json', 'tuner_result.txt', 'assessor_result.txt']
    to_remove = list(map(lambda file: 'naive_test/' + file, to_remove))
    remove_files(to_remove)

    proc = subprocess.run(['nnictl', 'create', '--config', 'naive_test/local.yml'])
    assert proc.returncode == 0, '`nnictl create` failed with code %d' % proc.returncode

    print('Spawning trials...')

    nnimanager_log_path = fetch_experiment_config(EXPERIMENT_URL)
    current_trial = 0

    for _ in range(60):
        time.sleep(1)

        tuner_status = read_last_line('naive_test/tuner_result.txt')
        assessor_status = read_last_line('naive_test/assessor_result.txt')
        experiment_status = check_experiment_status(nnimanager_log_path)

        assert tuner_status != 'ERROR', 'Tuner exited with error'
        assert assessor_status != 'ERROR', 'Assessor exited with error'

        if experiment_status:
            break

        if tuner_status is not None:
            for line in open('naive_test/tuner_result.txt'):
                if line.strip() == 'ERROR':
                    break
                trial = int(line.split(' ')[0])
                if trial > current_trial:
                    current_trial = trial
                    print('Trial #%d done' % trial)

    assert experiment_status, 'Failed to finish in 1 min'

    ss1 = json.load(open('naive_test/search_space.json'))
    ss2 = json.load(open('naive_test/tuner_search_space.json'))
    assert ss1 == ss2, 'Tuner got wrong search space'

    tuner_result = set(open('naive_test/tuner_result.txt'))
    expected = set(open('naive_test/expected_tuner_result.txt'))
    # Trials may complete before NNI gets assessor's result,
    # so it is possible to have more final result than expected
    assert tuner_result.issuperset(expected), 'Bad tuner result'

    assessor_result = set(open('naive_test/assessor_result.txt'))
    expected = set(open('naive_test/expected_assessor_result.txt'))
    assert assessor_result == expected, 'Bad assessor result'

if __name__ == '__main__':
    installed = (sys.argv[-1] != '--preinstall')
    setup_experiment(installed)
    try:
        run()
        # TODO: check the output of rest server
        print(GREEN + 'PASS' + CLEAR)
    except Exception as error:
        print(RED + 'FAIL' + CLEAR)
        print('%r' % error)
        traceback.print_exc()
        sys.exit(1)
    finally:
        subprocess.run(['nnictl', 'stop'])
