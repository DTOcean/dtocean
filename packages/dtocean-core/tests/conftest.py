import glob
import os
import shutil


def pytest_sessionstart(session):
    # Pickle data files and move to test directory
    data_dir = "test_data"
    test_dir = "tests"
    search_path = os.path.join(data_dir, "*.py")
    test_data_files = glob.glob(search_path)

    for test_data_path in test_data_files:
        src_path_root = os.path.splitext(test_data_path)[0]
        src_path = "{}.pkl".format(src_path_root)
        src_file = os.path.split(src_path)[1]
        dst_path = os.path.join(test_dir, src_file)
        dst_path = os.path.abspath(dst_path)

        sys_command = "python {}".format(test_data_path)
        os.system(sys_command)

        print("add test data: {}".format(dst_path))
        shutil.move(src_path, dst_path)

    # Move yaml definitions to test directory
    search_path = os.path.join(data_dir, "*.yaml")
    test_def_files = glob.glob(search_path)

    for test_def_path in test_def_files:
        src_file = os.path.split(test_def_path)[1]
        dst_path = os.path.join(test_dir, src_file)
        dst_path = os.path.abspath(dst_path)

        print("add data definitions: {}".format(dst_path))
        shutil.move(test_def_path, dst_path)
