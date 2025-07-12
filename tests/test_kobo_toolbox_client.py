import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from Kobo.kobo_toolbox_client import KoboToolboxClient

class TestKoboToolboxClient(unittest.TestCase):

    @patch('Kobo.kobo_toolbox_client.KoboExtractor')
    def setUp(self, MockKoboExtractor):
        """Set up a mock KoboToolbox client and sample data."""
        
        # Mock the KoboExtractor instance
        self.mock_kobo = MockKoboExtractor.return_value
        self.client = KoboToolboxClient(url="https://fake.kobo.com", token="fake_token")

        # Sample raw submission data from the API
        self.mock_submission_data = {
            'results': [
                {
                    'gender': '1',
                    'satisfaction': 'option_1',
                    'reasons': 'tech_skills confidence' # Space-separated raw values
                },
                {
                    'gender': '2',
                    'satisfaction': 'option_2',
                    'reasons': 'networking'
                }
            ]
        }

        # Sample form asset definition from the API
        self.mock_asset_data = {
            'content': {
                'survey': [
                    {'type': 'select_one', '$xpath': 'gender', 'label': ['Gender'], 'select_from_list_name': 'gender_list'},
                    {'type': 'select_one', '$xpath': 'satisfaction', 'label': ['Satisfaction'], 'select_from_list_name': 'satisfaction_list'},
                    {'type': 'select_multiple', '$xpath': 'reasons', 'label': ['Reasons'], 'select_from_list_name': 'reasons_list'}
                ],
                'choices': [
                    {'list_name': 'gender_list', 'name': '1', 'label': ['Female']},
                    {'list_name': 'gender_list', 'name': '2', 'label': ['Male']},
                    {'list_name': 'satisfaction_list', 'name': 'option_1', 'label': ['Happy']},
                    {'list_name': 'satisfaction_list', 'name': 'option_2', 'label': ['Sad']},
                    {'list_name': 'reasons_list', 'name': 'tech_skills', 'label': ['Technical Skills']},
                    {'list_name': 'reasons_list', 'name': 'confidence', 'label': ['Confidence']},
                    {'list_name': 'reasons_list', 'name': 'networking', 'label': ['Networking']}
                ]
            }
        }

    def test_get_submissions_with_labels(self):
        """
        Test that get_submissions correctly processes raw data into a labeled DataFrame,
        handling both single and multiple-choice questions.
        """
        # Configure the mock methods to return our sample data
        self.mock_kobo.get_data.return_value = self.mock_submission_data
        self.mock_kobo.get_asset.return_value = self.mock_asset_data

        # Call the method under test
        labeled_df = self.client.get_submissions(form_uid="fake_form_id", use_labels=True)

        # --- Assertions ---
        
        # 1. Check that the columns are renamed to their labels
        expected_columns = ['Gender', 'Satisfaction', 'Reasons']
        self.assertListEqual(list(labeled_df.columns), expected_columns)

        # 2. Check the values for the first row
        first_row = labeled_df.iloc[0]
        self.assertEqual(first_row['Gender'], 'Female')
        self.assertEqual(first_row['Satisfaction'], 'Happy')
        # Check that the multi-select answers are correctly mapped and joined
        self.assertEqual(first_row['Reasons'], 'Technical Skills, Confidence')

        # 3. Check the values for the second row
        second_row = labeled_df.iloc[1]
        self.assertEqual(second_row['Gender'], 'Male')
        self.assertEqual(second_row['Satisfaction'], 'Sad')
        self.assertEqual(second_row['Reasons'], 'Networking')

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
