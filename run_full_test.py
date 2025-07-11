import os
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Any, Generator
from requests.exceptions import RequestException
from dataclasses import dataclass
import traceback # Import traceback module

# --- Start of Kobo/form_info.py content ---
@dataclass
class FormInfo:
    uid: str
    name: str
    metadata: Dict[str, Any]
# --- End of Kobo/form_info.py content ---

# --- Start of Kobo/submission_result.py content ---
class SubmissionResult:
    def __init__(
        self,
        main_data: pd.DataFrame,
        repeat_data: Dict[str, pd.DataFrame],
        joined_data: pd.DataFrame
    ):
        self.main_data = main_data
        self.repeat_data = repeat_data
        self.joined_data = joined_data
# --- End of Kobo/submission_result.py content ---

# --- Start of Kobo/kobo_toolbox_client.py content (modified for debugging) ---
from koboextractor import KoboExtractor

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
        print(f"  DEBUG: _flatten_and_label_submission called. labeled_result keys: {labeled_result.keys()}")
        print(f"  DEBUG: choice_lists keys: {choice_lists.keys()}")
        print(f"  DEBUG: questions keys: {questions.keys()}")

        # Add metadata fields directly
        for meta_key, meta_value in labeled_result.get('meta', {}).items():
            flat_data[meta_key] = meta_value
            print(f"    DEBUG: Added meta {meta_key}: {meta_value}")

        # Process actual question results
        for question_name, question_data in labeled_result.get('results', {}).items():
            print(f"    DEBUG: Inside loop - Processing question_name: {question_name}")
            print(f"    DEBUG: Inside loop - Type of question_data: {type(question_data)}")
            print(f"    DEBUG: Inside loop - question_data: {question_data}")

            if not isinstance(question_data, dict):
                flat_data[question_name] = question_data
                print(f"    DEBUG: question_data is not dict. Stored as is: {question_data}")
                continue

            question_label = question_data.get('label', question_name)
            answer_code = question_data.get('answer_code')
            
            # Find the question definition to get its type and select_from_list_name
            question_def = questions.get('questions', {}).get(question_name)
            
            question_type = question_def.get('type') if question_def else None # Get type from question_def

            print(f"    DEBUG: Processing question: {question_name}, Type: {question_type}, Answer Code: {answer_code}")

            answer = None
            
            if question_type and question_type.startswith('select_') and question_def:
                list_name = question_def.get('list_name') # Use 'list_name' from question_def
                relevant_choices_dict = choice_lists.get(list_name) # Use list_name directly as key
                
                print(f"    DEBUG: Question def list_name: {list_name}, Relevant choices dict found: {relevant_choices_dict is not None}")

                if relevant_choices_dict:
                    # Create mappings from both 'name' and 'sequence' to 'label'
                    name_to_label_map = {str(info_code): info['label'] for info_code, info in relevant_choices_dict.items()}
                    sequence_to_label_map = {info['sequence']: info['label'] for info_code, info in relevant_choices_dict.items() if 'sequence' in info}
                    
                    print(f"    DEBUG: Name to label map: {name_to_label_map}")
                    print(f"    DEBUG: Sequence to label map: {sequence_to_label_map}")

                    if question_type == 'select_multiple':
                        selected_codes = str(answer_code).split(' ') if answer_code else []
                        selected_labels = []
                        for code in selected_codes:
                            mapped_label = name_to_label_map.get(code)
                            if mapped_label is None and code.startswith('option_'):
                                try:
                                    seq_num = int(code.split('_')[1])
                                    mapped_label = sequence_to_label_map.get(seq_num)
                                except (ValueError, IndexError):
                                    pass # Not an option_X format or invalid
                            selected_labels.append(mapped_label if mapped_label is not None else code)
                        answer = ', '.join(filter(None, selected_labels))
                        print(f"    DEBUG: Select multiple - Selected codes: {selected_codes}, Mapped labels: {selected_labels}, Final answer: {answer}")
                    elif answer_code is not None:
                        # Try mapping by name first
                        answer = name_to_label_map.get(str(answer_code))
                        if answer is None and str(answer_code).startswith('option_'):
                            # If not found by name, try mapping by sequence
                            try:
                                seq_num = int(str(answer_code).split('_')[1])
                                answer = sequence_to_label_map.get(seq_num)
                            except (ValueError, IndexError):
                                pass # Not an option_X format or invalid
                        
                        if answer is None: # Fallback if still not mapped
                            answer = str(answer_code)

                        print(f"    DEBUG: Select one - Answer code: {answer_code}, Mapped answer: {answer}")
                    else:
                        answer = question_data.get('answer_label') # Fallback if answer_code is None
                        print(f"    DEBUG: Select (fallback) - Answer label: {answer}")
                else:
                    # Fallback if choice list not found for the given list_name
                    answer = question_data.get('answer_label', answer_code)
                    print(f"    DEBUG: Select (no relevant choices) - Answer: {answer}")
            else: # For non-select questions or if question_def not found
                answer = question_data.get('answer_label', answer_code)
                print(f"    DEBUG: Non-select/No question def - Answer: {answer}")
            
            flat_data[question_label] = answer
            print(f"    DEBUG: Final flat_data[{question_label}] = {answer}")
        return flat_data

    def _get_submissions_with_options(self, form_uid: str, use_labels: bool) -> 'SubmissionResult':
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        # Removed try-except here to allow full traceback in debug script
        data = self.kobo.get_data(form_uid)
        results = data.get('results', [])
        if not results:
            return SubmissionResult(pd.DataFrame(), {}, pd.DataFrame())

        if use_labels:
            asset = self.kobo.get_asset(form_uid)
            # MODIFIED: Print full choices data
            full_choices_response = self.kobo.get_choices(asset)
            print(f"  DEBUG: Full choices response from koboextractor.get_choices: {full_choices_response}")
            # Correctly extract choice_lists from the full response
            choice_lists = full_choices_response # The top-level response is the choice_lists dict itself
            questions = self.kobo.get_questions(asset, unpack_multiples=True)
            print(f"  DEBUG: Full questions response from koboextractor.get_questions: {questions}") # Added print for questions
            
            processed_results = []
            for i, result in enumerate(results):
                print(f"\n  DEBUG: Processing submission {i+1}/{len(results)}")
                labeled_result = self.kobo.label_result(
                    unlabeled_result=result,
                    choice_lists=choice_lists, # Pass the correctly extracted choice_lists
                    questions=questions,
                    unpack_multiples=True
                )
                print(f"  DEBUG: Labeled result from koboextractor.label_result (first 500 chars): {str(labeled_result)[:500]}")
                flat_labeled_result = self._flatten_and_label_submission(labeled_result, choice_lists, questions)
                processed_results.append(flat_labeled_result)
            
            main_df = pd.DataFrame(processed_results)
        else:
            main_df = pd.DataFrame(results)

        return SubmissionResult(main_df, {}, main_df.copy())

    def get_all_submissions(self, form_uid: str, use_labels: bool = True) -> Generator[pd.DataFrame, None, None]:
        results_df = self._get_submissions_with_options(form_uid, use_labels).main_data
        if not results_df.empty:
            yield results_df

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
# --- End of Kobo/kobo_toolbox_client.py content ---


# --- Main execution logic (from notebook) ---
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8') # Ensure UTF-8 output

    load_dotenv()

    KOBO_API_URL = os.getenv("KOBO_API_URL", "https://kf.kobotoolbox.org/")
    KOBO_API_TOKEN = os.getenv("KOBO_API_TOKEN")

    if not KOBO_API_TOKEN:
        print("KOBO_API_TOKEN not found in environment variables. Please set it in your .env file.")
        exit(1)

    kobo_client = KoboToolboxClient(
        url=KOBO_API_URL,
        token=KOBO_API_TOKEN
    )

    try:
        forms = kobo_client.get_all_forms()
        if forms:
            first_form_uid = forms[0].uid
            print(f"Fetching submissions for form: {forms[0].name} ({first_form_uid})")

            print("\n--- DEBUGGING: Raw KoboExtractor Data and Response ---")
            raw_data_response = kobo_client.kobo.get_data(first_form_uid)
            print("Full Raw Data Response from kobo.get_data:", raw_data_response)

            if hasattr(kobo_client.kobo, 'last_response') and kobo_client.kobo.last_response is not None:
                print("Last HTTP Response Status Code:", kobo_client.kobo.last_response.status_code)
                print("Last HTTP Response Headers:", dict(kobo_client.kobo.last_response.headers))
                try:
                    print("Last HTTP Response Text (truncated):", kobo_client.kobo.last_response.text[:500].encode('utf-8', 'replace').decode('utf-8'))
                except Exception as e:
                    print(f"Error printing response text: {e}")
                    print("Attempting to print raw bytes (truncated):", kobo_client.kobo.last_response.content[:500])
            else:
                print("kobo_client.kobo.last_response not available.")
            print("--- END DEBUGGING ---\n")
            
            submissions_df = kobo_client.get_submissions(first_form_uid)
            print("Submissions DataFrame Head:\n", submissions_df.head())

        else:
            print("No forms found.")
    except Exception as e:
        print(f'\nError occurred while fetching submissions: {e}')