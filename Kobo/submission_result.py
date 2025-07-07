import pandas as pd
from typing import Dict

class SubmissionResult:
    """Helper class to store submission data results."""
    
    def __init__(
        self,
        main_data: pd.DataFrame,
        repeat_data: Dict[str, pd.DataFrame],
        joined_data: pd.DataFrame
    ):
        self.main_data = main_data
        self.repeat_data = repeat_data
        self.joined_data = joined_data