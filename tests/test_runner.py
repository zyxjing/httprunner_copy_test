import requests
from httprunner import utils
from tests.base import ApiServerUnittest
from httprunner import utils
import os
from httprunner import runner

class TestRunner(ApiServerUnittest):

    def test_run_sign_testcase_success(self):
        current_path = os.getcwd()
        case_json_file =os.path.join(current_path, 'tests\\data\\get_token.json')
        case_json = utils.load_test_cases(case_json_file)
        success, diff_content = runner.run_single_testcase(case_json)
        self.assertTrue(success)
        self.assertEqual(diff_content, {})
        
if __name__ == "__main__":
    import unittest
    unittest.main()