import sys
import os
from args import *
import csv
import json

MVN_CMD = 'mvn'
MVN_OPT_FILE = '-f'
MVN_POM_FILE = 'pom.xml'
MVN_CLEAN_GOAL = 'clean'
MVN_TEST_GOAL = 'test'
MVN_INSTALL_GOAL = 'install'
MVN_SKIP_TEST = '-DskipTests'
MVN_BUILD_CP_GOAL = 'dependency:build-classpath'
MVN_OPT_PATH_CP_OUTPUT = '-Dmdep.outputFile=classpath'

CMD_DIFF_TEST_SELECTION = 'eu.stamp-project:dspot-diff-test-selection:3.1.1-SNAPSHOT:list'
CMD_DIFF_INSTRUMENT = 'fr.davidson:diff-jjoules:instrument'
OPT_PATH_DIR_SECOND_VERSION = '-Dpath-dir-second-version='

OPT_TEST = '-Dtest='
OPT_TEST_LISTS = '-Dtests-list='
VALUE_TEST_LISTS = 'testsThatExecuteTheChange.csv'

def run_command(cmd):
    print(cmd)
    os.system(cmd)

def run_mvn_install(path):
    run_command(' '.join([
        MVN_CMD,
        MVN_OPT_FILE,
        path + '/' + MVN_POM_FILE,
        MVN_CLEAN_GOAL,
        MVN_INSTALL_GOAL,
        MVN_SKIP_TEST,
    ]))

def run_mvn_test(path, tests_to_execute):
    run_command(' '.join([
        MVN_CMD,
        MVN_OPT_FILE,
        path + '/' + MVN_POM_FILE,
        MVN_CLEAN_GOAL,
        MVN_TEST_GOAL,
        OPT_TEST + ','.join([test + '#' + '+'.join(tests_to_execute[test]) for test in tests_to_execute]),
    ]))

def run_mvn_build_cp(path):
    run_command(' '.join([
        MVN_CMD,
        MVN_OPT_FILE,
        path + '/' + MVN_POM_FILE,
        MVN_CLEAN_GOAL,
        MVN_TEST_GOAL,
        MVN_SKIP_TEST,
        MVN_BUILD_CP_GOAL,
        MVN_OPT_PATH_CP_OUTPUT
    ]))

def run_mvn_test_selection(path_first_version, path_second_version):
    run_command(
         ' '.join([
            MVN_CMD,
            MVN_OPT_FILE,
            path_first_version + '/' + MVN_POM_FILE,
            MVN_CLEAN_GOAL,
            CMD_DIFF_TEST_SELECTION,
            OPT_PATH_DIR_SECOND_VERSION + path_second_version,
        ])
    )

def run_mvn_instrument_jjoules(path_first_version, path_second_version):
    run_command(
         ' '.join([
            MVN_CMD,
            MVN_OPT_FILE,
            path_first_version + '/' + MVN_POM_FILE,
            CMD_DIFF_INSTRUMENT,
            OPT_TEST_LISTS + VALUE_TEST_LISTS,
            OPT_PATH_DIR_SECOND_VERSION + path_second_version
        ])
    )

def get_path_to_selected_tests_csv_file(output_path):
    for dirName, subdirList, fileList in os.walk(output_path):
        for file in fileList:
            if file == VALUE_TEST_LISTS:
                return dirName + '/' + VALUE_TEST_LISTS

def get_tests_to_execute(output_path):
    path = get_path_to_selected_tests_csv_file(output_path)
    tests_to_execute = {}
    with open(path, 'r') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        for line in file:
            tests_to_execute[line[0]] = line[1:]
    return tests_to_execute

def get_path_to_jjoules_report_folder(root_path_project):
    for dirName, subdirList, fileList in os.walk(root_path_project):
        for subdir in subdirList:
            if subdir == 'jjoules-reports':
                return dirName + '/' + subdir

def read_json(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    return data

CPU_MJ_KEY = 'package|uJ'
DURATION_NS_KEY = 'duration|ns'
DRAM_MJ_KEY = 'dram|uJ'

def get_energy_data(data):
    return {
        'energy': data[CPU_MJ_KEY],
        'duration': data[DURATION_NS_KEY],
        'dram': data[DRAM_MJ_KEY],
    } if data[CPU_MJ_KEY] > 0 else {}

def get_fullqualified_name_test(json_file):
    return json_file.split('.json')[0]

def avg_on_each_field(entry_a, entry_b):
    avg_entry = {}
    for e in entry_a:
        avg_entry[e] = (entry_a[e] + entry_b[e]) / 2
    return avg_entry

def collect_data(root_path_project, result):
    path_to_jjoules_report = get_path_to_jjoules_report_folder(root_path_project)
    for file in os.listdir(path_to_jjoules_report):
        data = get_energy_data(read_json(path_to_jjoules_report + '/' + file))
        name = get_fullqualified_name_test(file)
        if name in result:
            result[name] = avg_on_each_field(result[name], data)
        else:
            result[name] = data
    return result

def write_json(path_to_json, data):
    with open(path_to_json, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))

def run_tests(nb_iteration, first_version_path, second_version_path, tests_to_execute):
    result_v1 = {}
    result_v2 = {}
    for i in range(nb_iteration):
        run_mvn_test(first_version_path, tests_to_execute)
        result_v1 = collect_data(first_version_path, result_v1)
        run_mvn_test(second_version_path, tests_to_execute)
        result_v2 = collect_data(second_version_path, result_v2)
    write_json('avg_v1.json', result_v1)
    write_json('avg_v2.json', result_v2)
    delta_acc = 0
    for name in result_v1:
        if name in result_v2:
            if 'energy' in result_v1[name] and 'energy' in result_v2[name]:
                delta_acc = result_v2[name]['energy'] - result_v1[name]['energy']
    print(delta_acc)

if __name__ == '__main__':

    args = RunArgs().build_parser().parse_args()

    first_version_path = args.first_version_path
    second_version_path = args.second_version_path
    nb_iteration = args.iteration

    run_mvn_install(first_version_path)
    run_mvn_install(second_version_path)

    run_mvn_test_selection(first_version_path, second_version_path)

    run_mvn_build_cp(first_version_path)
    run_mvn_build_cp(second_version_path)
    run_mvn_instrument_jjoules(first_version_path, second_version_path)
    run_tests(nb_iteration, first_version_path, second_version_path, get_tests_to_execute(first_version_path))