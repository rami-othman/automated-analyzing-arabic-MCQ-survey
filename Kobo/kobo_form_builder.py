import json
from typing import List, Optional
import pandas as pd

class KoboFormBuilder:
    """Builds Kobo forms from questions and answers"""
    
    def __init__(self, title: str = "My Survey"):
        self.title = title
        self.content = {
            "survey": [],
            "choices": [],
            "settings": {
                "id_string": title.lower().replace(" ", "_"),
                "form_title": title
            }
        }
    
    def add_text_question(self, name: str, label: str, required: bool = False) -> None:
        """Add a text input question"""
        question = {
            "type": "text",
            "name": name,
            "label": [label],
            "required": required
        }
        self.content["survey"].append(question)
    
    def add_select_question(self, name: str, label: str, options: List[str], 
                           required: bool = False, appearance: Optional[str] = None) -> None:
        """Add a select question with multiple choices"""
        choice_list_name = f"{name}_choices"
        
        # Add choices
        for i, option in enumerate(options):
            self.content["choices"].append({
                "list_name": choice_list_name,
                "name": f"option_{i}",
                "label": [option]
            })
        
        # Add question
        question = {
            "type": "select_one",
            "name": name,
            "label": [label],
            "required": required,
            "select_from_list_name": choice_list_name
        }
        
        if appearance:
            question["appearance"] = appearance
            
        self.content["survey"].append(question)
    
    def add_multiselect(self, name: str, label: str, options: List[str],
                       required: bool = False) -> None:
        """Add a multiple select question"""
        choice_list_name = f"{name}_choices"
        
        # Add choices
        for i, option in enumerate(options):
            self.content["choices"].append({
                "list_name": choice_list_name,
                "name": f"option_{i}",
                "label": [option]
            })
        
        # Add question
        self.content["survey"].append({
            "type": "select_multiple",
            "name": name,
            "label": [label],
            "required": required,
            "select_from_list_name": choice_list_name
        })
    
    def to_json(self) -> str:
        """Export form as JSON string"""
        return json.dumps(self.content, indent=2)
    
    def to_xlsform(self, filename: str) -> None:
        """Export form to XLSForm format using pyxform"""
        try:
            survey_df = pd.DataFrame(self.content['survey'])
            choices_df = pd.DataFrame(self.content['choices'])
            settings_df = pd.DataFrame([self.content['settings']])

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                survey_df.to_excel(writer, sheet_name='survey', index=False)
                choices_df.to_excel(writer, sheet_name='choices', index=False)
                settings_df.to_excel(writer, sheet_name='settings', index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to create XLSForm: {str(e)}")