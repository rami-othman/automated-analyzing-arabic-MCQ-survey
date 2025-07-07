from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FormInfo:
    """
    Data class representing a Kobo form's basic information.
    
    Attributes:
        uid: The unique identifier of the form
        name: The display name of the form
        metadata: Additional metadata about the form
    """
    uid: str
    name: str
    metadata: Dict[str, Any]