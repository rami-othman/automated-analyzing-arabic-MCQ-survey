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
                'formhub/uuid': '1e91a958e62d444faac93333f9fb7fc5',
                'gender': 'option_0',
                'age_group': 'option_1',
                'governorate': 'option_0',
                'education_level': 'option_2',
                'employment_status': 'option_0',
                'specialization': 'option_0',
                'satisfaction_overall': 'option_1',
                'satisfaction_access': 'option_2',
                'satisfaction_support': 'option_1',
                'suggestions': 'option_1',
                'fruit_question': 'apple',
                'color_question': 'red',
                'multiple_choice_question': 'option_a option_c' # Raw data for select_multiple
            }]
        }

        self.mock_kobo_instance.get_asset.return_value = {'uid': form_uid, 'name': 'Test Form'}

        self.mock_kobo_instance.get_choices.return_value = {
            'choices': {
                'fruit_question': [
                    {'name': 'apple', 'label': 'Apple'},
                    {'name': 'banana', 'label': 'Banana'}
                ],
                'color_question': [
                    {'name': 'red', 'label': 'Red'},
                    {'name': 'blue', 'label': 'Blue'}
                ],
                'multiple_choice_question': [
                    {'name': 'option_a', 'label': 'Option A Text'},
                    {'name': 'option_b', 'label': 'Option B Text'},
                    {'name': 'option_c', 'label': 'Option C Text'}
                ],
                'gender': [
                    {'name': 'option_0', 'label': 'ذكر'},
                    {'name': 'option_1', 'label': 'أنثى'}
                ],
                'age_group': [
                    {'name': 'option_0', 'label': 'أقل من 18'},
                    {'name': 'option_1', 'label': '18-24'},
                    {'name': 'option_2', 'label': '25-34'},
                    {'name': 'option_3', 'label': '35-44'},
                    {'name': 'option_4', 'label': '45 فأكثر'}
                ],
                'governorate': [
                    {'name': 'option_0', 'label': 'دمشق'},
                    {'name': 'option_1', 'label': 'ريف دمشق'},
                    {'name': 'option_2', 'label': 'حلب'},
                    {'name': 'option_3', 'label': 'حمص'},
                    {'name': 'option_4', 'label': 'حماة'},
                    {'name': 'option_5', 'label': 'اللاذقية'},
                    {'name': 'option_6', 'label': 'طرطوس'},
                    {'name': 'option_7', 'label': 'إدلب'},
                    {'name': 'option_8', 'label': 'درعا'},
                    {'name': 'option_9', 'label': 'القنيطرة'},
                    {'name': 'option_10', 'label': 'دير الزور'},
                    {'name': 'option_11', 'label': 'الحسكة'},
                    {'name': 'option_12', 'label': 'الرقة'},
                    {'name': 'option_13', 'label': 'السويداء'}
                ],
                'education_level': [
                    {'name': 'option_0', 'label': 'ثانوي أو أقل'},
                    {'name': 'option_1', 'label': 'دبلوم'},
                    {'name': 'option_2', 'label': 'بكالوريوس'},
                    {'name': 'option_3', 'label': 'ماجستير'},
                    {'name': 'option_4', 'label': 'دكتوراه'}
                ],
                'employment_status': [
                    {'name': 'option_0', 'label': 'طالب'},
                    {'name': 'option_1', 'label': 'موظف'},
                    {'name': 'option_2', 'label': 'باحث عن عمل'},
                    {'name': 'option_3', 'label': 'عمل حر'},
                    {'name': 'option_4', 'label': 'أخرى'}
                ],
                'specialization': [
                    {'name': 'option_0', 'label': 'هندسة حاسوب'},
                    {'name': 'option_1', 'label': 'ذكاء اصطناعي'},
                    {'name': 'option_2', 'label': 'إدارة أعمال'},
                    {'name': 'option_3', 'label': 'اقتصاد'},
                    {'name': 'option_4', 'label': 'علوم اجتماعية'},
                    {'name': 'option_5', 'label': 'تربية'},
                    {'name': 'option_6', 'label': 'أخرى'}
                ],
                'satisfaction_overall': [
                    {'name': 'option_0', 'label': 'راضٍ جدًا'},
                    {'name': 'option_1', 'label': 'راضٍ'},
                    {'name': 'option_2', 'label': 'محايد'},
                    {'name': 'option_3', 'label': 'غير راضٍ'},
                    {'name': 'option_4', 'label': 'غير راضٍ أبدًا'}
                ],
                'satisfaction_access': [
                    {'name': 'option_0', 'label': 'سهل جدًا'},
                    {'name': 'option_1', 'label': 'سهل'},
                    {'name': 'option_2', 'label': 'متوسط'},
                    {'name': 'option_3', 'label': 'صعب'},
                    {'name': 'option_4', 'label': 'صعب جدًا'}
                ],
                'satisfaction_support': [
                    {'name': 'option_0', 'label': 'ممتاز'},
                    {'name': 'option_1', 'label': 'جيد جدًا'},
                    {'name': 'option_2', 'label': 'جيد'},
                    {'name': 'option_3', 'label': 'ضعيف'},
                    {'name': 'option_4', 'label': 'سيء جدًا'}
                ],
                'suggestions': [
                    {'name': 'option_0', 'label': 'نعم، لدي اقتراح'},
                    {'name': 'option_1', 'label': 'لا يوجد لدي اقتراح'}
                ]
            }
        }

        self.mock_kobo_instance.get_questions.return_value = {
            'questions': [
                {'name': 'fruit_question', 'label': 'Favorite Fruit', 'type': 'select_one', 'select_from_list_name': 'fruit_question'},
                {'name': 'color_question', 'label': 'Favorite Color', 'type': 'select_one', 'select_from_list_name': 'color_question'},
                {'name': 'multiple_choice_question', 'label': 'Select Multiple', 'type': 'select_multiple', 'select_from_list_name': 'multiple_choice_question'},
                {'name': 'gender', 'label': 'ما هو جنسك؟', 'type': 'select_one', 'select_from_list_name': 'gender'},
                {'name': 'age_group', 'label': 'ما هو فئتك العمرية؟', 'type': 'select_one', 'select_from_list_name': 'age_group'},
                {'name': 'governorate', 'label': 'في أي محافظة تعيش؟', 'type': 'select_one', 'select_from_list_name': 'governorate'},
                {'name': 'education_level', 'label': 'ما هو مستواك التعليمي؟', 'type': 'select_one', 'select_from_list_name': 'education_level'},
                {'name': 'employment_status', 'label': 'ما هو وضعك الوظيفي؟', 'type': 'select_one', 'select_from_list_name': 'employment_status'},
                {'name': 'specialization', 'label': 'ما هو تخصصك الأكاديمي؟', 'type': 'select_one', 'select_from_list_name': 'specialization'},
                {'name': 'satisfaction_overall', 'label': 'كيف تقيم تجربتك العامة مع الخدمات التي حصلت عليها؟', 'type': 'select_one', 'select_from_list_name': 'satisfaction_overall'},
                {'name': 'satisfaction_access', 'label': 'ما مدى سهولة الوصول إلى الخدمات المقدمة؟', 'type': 'select_one', 'select_from_list_name': 'satisfaction_access'},
                {'name': 'satisfaction_support', 'label': 'ما مدى جودة الدعم الذي حصلت عليه أثناء استخدام الخدمة؟', 'type': 'select_one', 'select_from_list_name': 'satisfaction_support'},
                {'name': 'suggestions', 'label': 'هل لديك اقتراحات لتحسين الخدمات؟', 'type': 'select_one', 'select_from_list_name': 'suggestions'}
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
                # Find question_info from the questions dict (which is keyed by question name)
                question_info = questions.get('questions', {}).get(key)

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
                        list_name = question_info.get('list_name') # Use list_name from question_info
                        if list_name and list_name in choice_lists:
                            for choice_code, choice_info in choice_lists[list_name].items():
                                choices_data[choice_code] = {
                                    'label': choice_info['label'],
                                    'answer_label': 'Yes' if choice_code in selected_options else 'No'
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
        self.assertIn('ما هو جنسك؟', df.columns)
        self.assertIn('ما هو فئتك العمرية؟', df.columns)
        self.assertIn('في أي محافظة تعيش؟', df.columns)
        self.assertIn('ما هو مستواك التعليمي؟', df.columns)
        self.assertIn('ما هو وضعك الوظيفي؟', df.columns)
        self.assertIn('ما هو تخصصك الأكاديمي؟', df.columns)
        self.assertIn('كيف تقيم تجربتك العامة مع الخدمات التي حصلت عليها؟', df.columns)
        self.assertIn('ما مدى سهولة الوصول إلى الخدمات المقدمة؟', df.columns)
        self.assertIn('ما مدى جودة الدعم الذي حصلت عليه أثناء استخدام الخدمة؟', df.columns)
        self.assertIn('هل لديك اقتراحات لتحسين الخدمات؟', df.columns)
        self.assertIn('_id', df.columns) # Check for metadata
        self.assertIn('_submission_time', df.columns) # Check for metadata
        
        self.assertEqual(df.iloc[0]['Favorite Fruit'], 'Apple')
        self.assertEqual(df.iloc[0]['Favorite Color'], 'Red')
        self.assertEqual(df.iloc[0]['Select Multiple'], 'Option A Text, Option C Text')
        self.assertEqual(df.iloc[0]['ما هو جنسك؟'], 'ذكر')
        self.assertEqual(df.iloc[0]['ما هو فئتك العمرية؟'], '18-24')
        self.assertEqual(df.iloc[0]['في أي محافظة تعيش؟'], 'دمشق')
        self.assertEqual(df.iloc[0]['ما هو مستواك التعليمي؟'], 'بكالوريوس')
        self.assertEqual(df.iloc[0]['ما هو وضعك الوظيفي؟'], 'طالب')
        self.assertEqual(df.iloc[0]['ما هو تخصصك الأكاديمي؟'], 'هندسة حاسوب')
        self.assertEqual(df.iloc[0]['كيف تقيم تجربتك العامة مع الخدمات التي حصلت عليها��'], 'راضٍ')
        self.assertEqual(df.iloc[0]['ما مدى سهولة الوصول إلى الخدمات المقدمة؟'], 'متوسط')
        self.assertEqual(df.iloc[0]['ما مدى جودة الدعم الذي حصلت عليه أثناء استخدام الخدمة؟'], 'جيد جدًا')
        self.assertEqual(df.iloc[0]['هل لديك اقتراحات لتحسين الخدمات؟'], 'لا يوجد لدي اقتراح')
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