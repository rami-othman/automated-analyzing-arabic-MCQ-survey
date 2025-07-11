from koboextractor import KoboExtractor
import pandas as pd
from typing import Dict, List, Tuple, Any, Generator
from requests.exceptions import RequestException
from .form_info import FormInfo
from .submission_result import SubmissionResult

class KoboToolboxClient:
    """A comprehensive client for interacting with KoboToolbox API using kobo-extractor."""

    def __init__(self, url: str, token: str, api_version: int = 2):
        self.base_url = url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v{api_version}"
        self.token = token
        try:
            self.kobo = KoboExtractor(token, self.api_url)
        except RequestException as e:
            raise ConnectionError(f"Failed to initialize KoboToolbox client: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred during client initialization: {str(e)}")

    def get_all_forms(self) -> List[FormInfo]:
        try:
            assets = self.kobo.list_assets()
            return [
                FormInfo(
                    uid=asset.get('uid'),
                    name=asset.get('name'),
                    metadata=asset
                )
                for asset in assets.get('results', [])
            ]
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching forms: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while fetching forms: {str(e)}")

    def get_form_details(self, form_uid: str) -> Dict[str, Any]:
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        try:
            asset = self.kobo.get_asset(form_uid)
            return asset
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching form details: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while fetching form details: {str(e)}")

    def get_submissions(self, form_uid: str, use_labels: bool = True) -> pd.DataFrame:
        return self._get_submissions_with_options(form_uid, use_labels).main_data

    def get_submissions_with_repeats(self, form_uid: str, use_labels: bool = True) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        result = self._get_submissions_with_options(form_uid, use_labels)
        return result.main_data, result.repeat_data

    def get_joined_submissions(self, form_uid: str, use_labels: bool = True) -> pd.DataFrame:
        return self._get_submissions_with_options(form_uid, use_labels).joined_data

    def _flatten_and_label_submission(self, labeled_result: Dict[str, Any], choice_lists: Dict[str, Any], questions: Dict[str, Any]) -> Dict[str, Any]:
        flat_data = {}

        # Add metadata fields directly
        for meta_key, meta_value in labeled_result.get('meta', {}).items():
            flat_data[meta_key] = meta_value

        # Process actual question results
        for question_name, question_data in labeled_result.get('results', {}).items():
            question_label = question_data.get('label', question_name)
            question_type = question_data.get('type')
            answer_code = question_data.get('answer_code')
            
            answer = None
            if question_type and question_type.startswith('select_'):
                # Find the correct choice list name for this question
                choice_list_name = None
                for q in questions.get('questions', []):
                    if q.get('name') == question_name:
                        choice_list_name = q.get('select_from_list_name')
                        break
                
                if choice_list_name and choice_list_name in choice_lists:
                    choices_map = {choice['name']: choice['label'] for choice in choice_lists[choice_list_name]}

                    if question_type == 'select_multiple':
                        # The answer_code for select_multiple is a space-separated string of selected options
                        selected_codes = answer_code.split(' ') if answer_code else []
                        selected_labels = [choices_map.get(code, code) for code in selected_codes if code]
                        answer = ', '.join(filter(None, selected_labels))
                    elif answer_code is not None:
                        # For select_one, map the single answer_code to its label
                        answer = choices_map.get(answer_code, answer_code)
                    else:
                        answer = question_data.get('answer_label') # Fallback if answer_code is None
                else:
                    # Fallback if choice list not found or question type is not select
                    answer = question_data.get('answer_label', answer_code)
            else: # For non-select questions, use answer_label or answer_code
                answer = question_data.get('answer_label', answer_code)
            
            flat_data[question_label] = answer
        return flat_data

    def _get_submissions_with_options(self, form_uid: str, use_labels: bool) -> 'SubmissionResult':
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            data = self.kobo.get_data(form_uid)
            results = data.get('results', [])
            if not results:
                return SubmissionResult(pd.DataFrame(), {}, pd.DataFrame())

            if use_labels:
                asset = self.kobo.get_asset(form_uid)
                choice_lists = self.kobo.get_choices(asset).get('choices', {})
                questions = self.kobo.get_questions(asset, unpack_multiples=True)
                
                processed_results = []
                for result in results:
                    labeled_result = self.kobo.label_result(
                        unlabeled_result=result,
                        choice_lists=choice_lists,
                        questions=questions,
                        unpack_multiples=True
                    )
                    flat_labeled_result = self._flatten_and_label_submission(labeled_result, choice_lists, questions)
                    processed_results.append(flat_labeled_result)
                
                main_df = pd.DataFrame(processed_results)
            else:
                main_df = pd.DataFrame(results)

            return SubmissionResult(main_df, {}, main_df.copy())
            
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching data: {str(e)}")
        except (AttributeError, KeyError, TypeError) as e:
            raise RuntimeError(f"Data processing error after fetch: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while fetching submissions: {str(e)}")

    def get_all_submissions(self, form_uid: str, use_labels: bool = True) -> Generator[pd.DataFrame, None, None]:
        try:
            results_df = self._get_submissions_with_options(form_uid, use_labels).main_data
            if not results_df.empty:
                yield results_df
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching data: {str(e)}")

    def export_form_data_to_csv(self, form_uid: str, output_path: str, use_labels: bool = True) -> str:
        data = self.get_submissions(form_uid, use_labels)
        data.to_csv(output_path, index=False)
        return output_path

    def export_form_data_to_excel(self, form_uid: str, output_path: str, use_labels: bool = True) -> str:
        data = self.get_submissions(form_uid, use_labels)
        data.to_excel(output_path, index=False)
        return output_path

    def get_form_data_as_csv(self, form_uid: str, use_labels: bool = True) -> str:
        return self.get_submissions(form_uid, use_labels).to_csv(index=False)
