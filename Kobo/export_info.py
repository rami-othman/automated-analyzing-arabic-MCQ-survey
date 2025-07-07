from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ExportInfo:
    uid: str
    status: str
    messages: List[str]
    result: Optional[str]
