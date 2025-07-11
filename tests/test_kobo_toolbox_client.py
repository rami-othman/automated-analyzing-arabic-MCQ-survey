import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from Kobo.kobo_toolbox_client import KoboToolboxClient

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from Kobo.kobo_toolbox_client import KoboToolboxClient

class TestKoboToolboxClient(unittest.TestCase):

    def setUp(self):
        # self.client will be initialized within each test method after patching
        pass

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_submissions_with_labels(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'aFakeFormUID'
        
        self.mock_kobo_instance.get_data.return_value = {
            'results': [{
                '_id': 1,
                'fruit_question': 'apple',
                'color_question': 'red',
                'multiple_choice_question': 'option_a option_c' # Raw data for select_multiple
            }]
        }

        self.mock_kobo_instance.get_asset.return_value = {'uid': form_uid, 'name': 'Test Form'}

        self.mock_kobo_instance.get_choices.return_value = {
            'choices': {
                'fruit_list': [
                    {'name': 'apple', 'label': 'Apple'},
                    {'name': 'banana', 'label': 'Banana'}
                ],
                'color_list': [
                    {'name': 'red', 'label': 'Red'},
                    {'name': 'blue', 'label': 'Blue'}
                ],
                'multi_list': [
                    {'name': 'option_a', 'label': 'Option A Text'},
                    {'name': 'option_b', 'label': 'Option B Text'},
                    {'name': 'option_c', 'label': 'Option C Text'}
                ]
            }
        }

        self.mock_kobo_instance.get_questions.return_value = {
            'questions': [
                {'name': 'fruit_question', 'label': 'Favorite Fruit', 'type': 'select_one', 'select_from_list_name': 'fruit_list'},
                {'name': 'color_question', 'label': 'Favorite Color', 'type': 'select_one', 'select_from_list_name': 'color_list'},
                {'name': 'multiple_choice_question', 'label': 'Select Multiple', 'type': 'select_multiple', 'select_from_list_name': 'multi_list'}
            ]
        }
        
        # Mock label_result to return the structure that _flatten_and_label_submission expects
        # This now accurately reflects the observed output from koboextractor.label_result
        def mock_label_result(unlabeled_result, choice_lists, questions, unpack_multiples):
            labeled = {
                'meta': {
                    '_id': unlabeled_result.get('_id'),
                    'formhub/uuid': unlabeled_result.get('formhub/uuid'),
                    '_submission_time': '2025-07-09T05:52:30' # Mock a timestamp
                },
                'results': {}
            }
            for key, value in unlabeled_result.items():
                if key.startswith(('_', 'meta/')):
                    continue # Skip these as they are handled by 'meta'

                question_info = None
                for q in questions.get('questions', []):
                    if q.get('name') == key:
                        question_info = q
                        break

                if question_info:
                    labeled['results'][key] = {
                        'label': question_info.get('label', key),
                        'type': question_info.get('type'),
                        'answer_code': value,
                        'answer_label': value # koboextractor.label_result often returns raw code here
                    }
                    if question_info.get('type') == 'select_multiple':
                        # Simulate the 'choices' sub-dictionary for select_multiple
                        choices_data = {}
                        selected_options = value.split(' ') if value else []
                        list_name = question_info.get('select_from_list_name')
                        if list_name and list_name in choice_lists:
                            for choice_item in choice_lists[list_name]:
                                choice_name = choice_item['name']
                                choice_label = choice_item['label']
                                choices_data[choice_name] = {
                                    'label': choice_label,
                                    'answer_label': 'Yes' if choice_name in selected_options else 'No'
                                }
                        labeled['results'][key]['choices'] = choices_data
                else:
                    # For questions not found in 'questions' (e.g., free text, numbers)
                    labeled['results'][key] = {
                        'label': key,
                        'type': 'text', # Default type
                        'answer_code': value,
                        'answer_label': value
                    }
            return labeled

        self.mock_kobo_instance.label_result.side_effect = mock_label_result

        df = self.client.get_submissions(form_uid=form_uid, use_labels=True)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # Assertions now check for the human-readable labels after _flatten_and_label_submission
        self.assertIn('Favorite Fruit', df.columns)
        self.assertIn('Favorite Color', df.columns)
        self.assertIn('Select Multiple', df.columns)
        self.assertIn('_id', df.columns) # Check for metadata
        self.assertIn('_submission_time', df.columns) # Check for metadata
        
        self.assertEqual(df.iloc[0]['Favorite Fruit'], 'Apple')
        self.assertEqual(df.iloc[0]['Favorite Color'], 'Red')
        self.assertEqual(df.iloc[0]['Select Multiple'], 'Option A Text, Option C Text')
        self.assertEqual(df.iloc[0]['_id'], 1)
        self.assertEqual(df.iloc[0]['_submission_time'], '2025-07-09T05:52:30')

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_submissions_no_labels(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'aFakeFormUID'
        expected_data = {
            '_id': [1],
            'question1': ['answer1'],
            'question2': ['answer2']
        }
        self.mock_kobo_instance.get_data.return_value = {
            'results': [
                {'_id': 1, 'question1': 'answer1', 'question2': 'answer2'}
            ]
        }

        df = self.client.get_submissions(form_uid=form_uid, use_labels=False)
        
        pd.testing.assert_frame_equal(df, pd.DataFrame(expected_data))
        self.mock_kobo_instance.get_asset.assert_not_called()
        self.mock_kobo_instance.get_choices.assert_not_called()
        self.mock_kobo_instance.get_questions.assert_not_called()
        self.mock_kobo_instance.label_result.assert_not_called()

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_all_forms(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        self.mock_kobo_instance.list_assets.return_value = {
            'results': [
                {'uid': 'form1_uid', 'name': 'Form 1', 'other_meta': 'data1'},
                {'uid': 'form2_uid', 'name': 'Form 2', 'other_meta': 'data2'}
            ]
        }
        forms = self.client.get_all_forms()
        self.assertEqual(len(forms), 2)
        self.assertEqual(forms[0].uid, 'form1_uid')
        self.assertEqual(forms[0].name, 'Form 1')
        self.assertEqual(forms[1].uid, 'form2_uid')
        self.assertEqual(forms[1].name, 'Form 2')

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_form_details(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'form_detail_uid'
        expected_details = {'uid': form_uid, 'name': 'Detailed Form', 'status': 'active'}
        self.mock_kobo_instance.get_asset.return_value = expected_details
        details = self.client.get_form_details(form_uid)
        self.assertEqual(details, expected_details)
        self.mock_kobo_instance.get_asset.assert_called_with(form_uid)

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_form_details_invalid_uid(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        with self.assertRaises(ValueError):
            self.client.get_form_details(None)
        with self.assertRaises(ValueError):
            self.client.get_form_details("")

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_submissions_empty_results(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'empty_form_uid'
        self.mock_kobo_instance.get_data.return_value = {'results': []}
        df = self.client.get_submissions(form_uid)
        self.assertTrue(df.empty)
        self.assertIsInstance(df, pd.DataFrame)

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_submissions_network_error(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        from requests.exceptions import RequestException
        self.mock_kobo_instance.get_data.side_effect = RequestException("Network issue")
        with self.assertRaisesRegex(RuntimeError, "Network error while fetching data"):
            self.client.get_submissions('some_uid')

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_all_submissions_generator(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'gen_form_uid'
        self.mock_kobo_instance.get_data.return_value = {
            'results': [{'_id': 1, 'q1': 'a1'}, {'_id': 2, 'q1': 'a2'}]
        }
        self.mock_kobo_instance.get_asset.return_value = {'uid': form_uid, 'name': 'Test Form'}
        self.mock_kobo_instance.get_choices.return_value = {'choices': {}}
        self.mock_kobo_instance.get_questions.return_value = {'questions': []}
        self.mock_kobo_instance.label_result.side_effect = lambda x, **kwargs: x # Passthrough for simplicity

        gen = self.client.get_all_submissions(form_uid, use_labels=False)
        df = next(gen)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['q1'], 'a1')
        self.assertEqual(df.iloc[1]['q1'], 'a2')
        with self.assertRaises(StopIteration):
            next(gen) # Ensure generator is exhausted

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_export_form_data_to_csv(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'csv_form_uid'
        output_path = 'test_output.csv'
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        
        # Mock get_submissions to return a DataFrame
        with patch('Kobo.kobo_toolbox_client.KoboToolboxClient.get_submissions', return_value=mock_df) as mock_get_submissions:
            # Mock pd.DataFrame.to_csv
            with patch.object(pd.DataFrame, 'to_csv') as mock_to_csv:
                result_path = self.client.export_form_data_to_csv(form_uid, output_path)
                mock_get_submissions.assert_called_once_with(form_uid, True)
                mock_to_csv.assert_called_once_with(output_path, index=False)
                self.assertEqual(result_path, output_path)

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_export_form_data_to_excel(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'excel_form_uid'
        output_path = 'test_output.xlsx'
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        
        # Mock get_submissions to return a DataFrame
        with patch('Kobo.kobo_toolbox_client.KoboToolboxClient.get_submissions', return_value=mock_df) as mock_get_submissions:
            # Mock pd.DataFrame.to_excel
            with patch.object(pd.DataFrame, 'to_excel') as mock_to_excel:
                result_path = self.client.export_form_data_to_excel(form_uid, output_path)
                mock_get_submissions.assert_called_once_with(form_uid, True)
                mock_to_excel.assert_called_once_with(output_path, index=False)
                self.assertEqual(result_path, output_path)

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def test_get_form_data_as_csv(self, MockKoboExtractor):
        self.mock_kobo_instance = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake-url.com", token="fake_token") # Initialize client here
        form_uid = 'get_csv_form_uid'
        expected_csv_string = """col1,col2\r\n1,a\r\n2,b\r\n"""
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        
        # Mock get_submissions to return a DataFrame
        with patch('Kobo.kobo_toolbox_client.KoboToolboxClient.get_submissions', return_value=mock_df) as mock_get_submissions:
            result_csv = self.client.get_form_data_as_csv(form_uid)
            mock_get_submissions.assert_called_once_with(form_uid, True)
            self.assertEqual(result_csv, expected_csv_string)


if __name__ == '__main__':
    unittest.main()