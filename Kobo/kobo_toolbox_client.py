import pykobo
import pandas as pd
from typing import Dict, List, Tuple, Any, Generator
from requests.exceptions import RequestException
from .form_info import FormInfo
from .submission_result import SubmissionResult

class KoboToolboxClient:
    """A comprehensive client for interacting with KoboToolbox API using pykobo."""
    
    def __init__(self, url: str, token: str, api_version: int = 2):
        """
        Initialize the KoboToolbox client.
        
        Args:
            url: KoboToolbox server URL (e.g., "https://kf.kobotoolbox.org/")
            token: API token for authentication
            api_version: API version to use (default is 2)
        """
        self.url = url.rstrip('/') + '/'
        self.token = token
        self.api_version = api_version
        self.manager = self._initialize_manager()
    
    def _initialize_manager(self) -> pykobo.Manager:
        """Initialize the pykobo Manager with proper error handling."""
        try:
            return pykobo.Manager(
                url=self.url,
                api_version=self.api_version,
                token=self.token
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize KoboToolbox manager: {str(e)}")

    # ======================
    # ASSETS/FORMS ENDPOINTS
    # ======================
    
    def get_all_forms(self) -> List[FormInfo]:
        """Get a list of all forms accessible with the current token."""
        try:
            forms = self.manager.get_forms()
            return [
                FormInfo(
                    uid=getattr(form, 'uid', ''),
                    name=getattr(form, 'metadata', {}).get('name', 'Unnamed Form'),
                    metadata=getattr(form, 'metadata', {})
                )
                for form in forms
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch forms: {str(e)}")
    
    def get_form_details(self, form_uid: str) -> Dict[str, Any]:
        """Get detailed metadata about a specific form/asset."""
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            form = self.manager.get_form(form_uid)
            if form is None:
                return {}
            return getattr(form, 'metadata', {})
        except Exception as e:
            raise RuntimeError(f"Failed to fetch form details: {str(e)}")

    # =====================
    # SUBMISSIONS ENDPOINTS
    # =====================
    
    def get_submissions(self, form_uid: str) -> pd.DataFrame:
        """Get main submissions DataFrame for a specific form."""
        return self._get_submissions_with_options(form_uid).main_data
    
    def get_submissions_with_repeats(self, form_uid: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Get main submissions DataFrame and repeat group DataFrames."""
        result = self._get_submissions_with_options(form_uid)
        return result.main_data, result.repeat_data
    
    def get_joined_submissions(self, form_uid: str) -> pd.DataFrame:
        """Get submissions with repeat groups joined to main data."""
        return self._get_submissions_with_options(form_uid).joined_data
    
    def _get_submissions_with_options(self, form_uid: str) -> 'SubmissionResult':
        """Internal method to handle all submission retrieval options."""
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            form = self.manager.get_form(form_uid)
            if form is None:
                raise RuntimeError(f"Form with UID {form_uid} not found")
                
            form.fetch_data()
            
            if not hasattr(form, 'data') or form.data is None:
                raise RuntimeError(f"No data available for form {form_uid}")
            
            main_df = form.data.copy()
            repeat_data = {}
            
            if hasattr(form, 'has_repeats') and form.has_repeats and hasattr(form, 'repeats'):
                for repeat_name, repeat_df in form.repeats.items():
                    if repeat_df is not None:
                        repeat_data[repeat_name] = repeat_df.copy()
            
            joined_df = main_df.copy()
            for repeat_name, repeat_df in repeat_data.items():
                if '_parent_index' in repeat_df.columns:
                    joined_df = pd.merge(
                        joined_df,
                        repeat_df,
                        how='left',
                        left_on='_index',
                        right_on='_parent_index',
                        suffixes=(None, f'_{repeat_name}')
                    )
            
            return SubmissionResult(main_df, repeat_data, joined_df)
            
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching data: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data: {str(e)}")
    
    def get_all_submissions(self, form_uid: str) -> Generator[pd.DataFrame, None, None]:
        """Generator that yields all submissions in batches."""
        offset = 0
        batch_size = 1000
        while True:
            batch = self.get_submissions(form_uid)
            if batch.empty:
                break
            yield batch
            offset += batch_size
    
    def export_form_data_to_csv(self, form_uid: str, output_path: str) -> str:
        """Export form data to CSV file."""
        data = self.get_submissions(form_uid)
        data.to_csv(output_path, index=False)
        return output_path
    
    def export_form_data_to_excel(self, form_uid: str, output_path: str) -> str:
        """Export form data to Excel file."""
        data = self.get_submissions(form_uid)
        data.to_excel(output_path, index=False)
        return output_path
    
    def get_form_data_as_csv(self, form_uid: str) -> str:
        """Get form data as CSV string."""
        return self.get_submissions(form_uid).to_csv(index=False)