from koboextractor import KoboExtractor
import pandas as pd
from typing import Dict, List, Tuple, Any, Generator, TypedDict
from requests.exceptions import RequestException
from .form_info import FormInfo
from .submission_result import SubmissionResult


class MappingInfo(TypedDict):
    """A type definition for the structure of the label mapping."""
    label: str
    type: str  # 'select_one' or 'select_multiple'
    choices: Dict[str, str]


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

    def _create_label_mapping(self, form_asset: Dict[str, Any]) -> Dict[str, MappingInfo]:
        """
        Creates a mapping from question names to their choice labels.
        e.g. {'gender': {'label': 'Gender', 'choices': {'1': 'Male'}}}
        """
        mapping: Dict[str, MappingInfo] = {}
        try:
            content = form_asset.get('content', {})
            survey = content.get('survey', [])
            choices = content.get('choices', [])
            
            choice_map: Dict[str, Dict[str, str]] = {}
            for choice in choices:
                list_name = choice.get('list_name')
                if list_name not in choice_map:
                    choice_map[list_name] = {}
                label = choice.get('label', [None])[0]
                if label:  # Ensure label is not None
                    choice_map[list_name][choice.get('name')] = label

            for question in survey:
                question_type = question.get('type', '')
                if question_type.startswith('select_'):
                    question_name = question.get('$xpath')
                    question_label = question.get('label', [question_name])[0]
                    list_name = question.get('select_from_list_name')
                    if list_name in choice_map:
                        mapping[question_name] = {
                            "label": question_label,
                            "type": question_type,
                            "choices": choice_map[list_name]
                        }
            return mapping
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Error creating label mapping from form asset: {e}")

    def _get_submissions_with_options(self, form_uid: str, use_labels: bool) -> 'SubmissionResult':
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            data = self.kobo.get_data(form_uid).get('results', [])
            if not data:
                return SubmissionResult(pd.DataFrame(), {}, pd.DataFrame())

            main_df = pd.DataFrame(data)

            if use_labels:
                asset = self.kobo.get_asset(form_uid)
                label_mapping = self._create_label_mapping(asset)
                
                df_labeled = main_df.copy()
                column_rename_map = {}

                for question_name, mapping_info in label_mapping.items():
                    if question_name in df_labeled.columns:
                        choices = mapping_info['choices']
                        # Handle multiple-choice questions differently
                        if mapping_info['type'] == 'select_multiple':
                            def map_multiple_choices(value):
                                if pd.isna(value) or value == '':
                                    return ''
                                # Raw data for multi-select is space-separated
                                answer_codes = str(value).split(' ')
                                labels = [choices.get(code, code) for code in answer_codes]
                                # Return as a clean, comma-separated string
                                return ', '.join(labels)
                            
                            df_labeled[question_name] = df_labeled[question_name].apply(map_multiple_choices)
                        else:
                            # Handle single-choice questions
                            df_labeled[question_name] = df_labeled[question_name].map(choices)
                        
                        column_rename_map[question_name] = mapping_info['label']
                
                df_labeled.rename(columns=column_rename_map, inplace=True)
                main_df = df_labeled

            return SubmissionResult(main_df, {}, main_df.copy())
            
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching data: {str(e)}")
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