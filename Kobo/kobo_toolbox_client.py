import pykobo
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any, Generator
from pykobo.form import KoboForm
from requests.exceptions import RequestException
from .form_info import FormInfo


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
        """
        Get a list of all forms accessible with the current token.
        """
        try:
            forms = self.manager.get_forms()
            form_info_list = []
            
            for form in forms:
                uid = getattr(form, 'uid', '')
                metadata = getattr(form, 'metadata', {})
                name = metadata.get('name', f'Unnamed Form ({uid[:8]}...)')
                
                form_info_list.append(
                    FormInfo(
                        uid=uid,
                        name=name,
                        metadata=metadata
                    )
                )
                
            return form_info_list
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch forms: {str(e)}")
    
    def get_form_details(self, form_uid: str) -> Dict[str, Any]:
        """
        Get detailed metadata about a specific form/asset.
        """
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            form = self.manager.get_form(form_uid)
            if form is None:
                raise RuntimeError(f"Form with UID {form_uid} not found")
            return getattr(form, 'metadata', {})
        except Exception as e:
            raise RuntimeError(f"Failed to fetch form details: {str(e)}")

    # =====================
    # SUBMISSIONS ENDPOINTS
    # =====================
    
    def get_submissions(
        self,
        form_uid: str,
        include_repeats: bool = False,
        join_repeats: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]]:
        """
        Get submissions for a specific form.
        """
        if not form_uid or not isinstance(form_uid, str):
            raise ValueError("form_uid must be a non-empty string")
        
        try:
            form: KoboForm | None = self.manager.get_form(form_uid)
            if form is None:
                raise RuntimeError(f"Form with UID {form_uid} not found")
                
            form.fetch_data()
            
            if not hasattr(form, 'data') or form.data is None:
                raise RuntimeError(f"No data available for form {form_uid}")
            
            main_df = form.data.copy()
            
            if not include_repeats:
                return main_df
            
            repeat_data: Dict[str, pd.DataFrame] = {}
            if hasattr(form, 'has_repeats') and form.has_repeats and hasattr(form, 'repeats'):
                for repeat_name, repeat_df in form.repeats.items():
                    if repeat_df is not None:
                        repeat_data[repeat_name] = repeat_df.copy()
            
            if not join_repeats:
                return main_df, repeat_data
            
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
            
            return joined_df
            
        except RequestException as e:
            raise RuntimeError(f"Network error while fetching data for form {form_uid}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for form {form_uid}: {str(e)}")
    
    def get_all_submissions(
        self,
        form_uid: str,
        batch_size: int = 1000,
        **kwargs: Any
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Generator that yields all submissions in batches.
        """
        offset = 0
        while True:
            batch = self.get_submissions(form_uid, **kwargs)
            if isinstance(batch, tuple):
                batch = batch[0]
            if batch.empty:
                break
            yield batch
            offset += batch_size
    
    def export_form_data(
        self,
        form_uid: str,
        output_format: str = 'csv',
        output_path: Optional[str] = None,
        **kwargs: Any
    ) -> Optional[str]:
        """
        Export form data to a file.
        """
        if output_format not in ('csv', 'excel'):
            raise ValueError("output_format must be 'csv' or 'excel'")
        
        data = self.get_submissions(form_uid, **kwargs)
        if isinstance(data, tuple):
            data = data[0]
        
        if output_path is None:
            if output_format == 'csv':
                return data.to_csv(index=False)
            raise ValueError("Cannot return Excel data as string")
        
        if output_format == 'csv':
            data.to_csv(output_path, index=False)
        else:
            data.to_excel(output_path, index=False)
        
        return output_path