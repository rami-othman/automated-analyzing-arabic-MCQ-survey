import os
import json
from dotenv import load_dotenv
from Kobo.kobo_toolbox_client import KoboToolboxClient

def debug_kobo_form_structure():
    """
    Connects to KoboToolbox, fetches the first form's full definition,
    and saves it to a JSON file to understand its structure.
    """
    load_dotenv()

    KOBO_API_URL = os.getenv("KOBO_API_URL", "https://kf.kobotoolbox.org/")
    KOBO_API_TOKEN = os.getenv("KOBO_API_TOKEN")

    if not KOBO_API_TOKEN:
        print("Error: KOBO_API_TOKEN not found.")
        return

    print("Initializing KoboToolbox client...")
    try:
        kobo_client = KoboToolboxClient(url=KOBO_API_URL, token=KOBO_API_TOKEN)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    try:
        print("Fetching forms...")
        forms = kobo_client.get_all_forms()
        if not forms:
            print("No forms found.")
            return

        first_form_uid = forms[0].uid
        print(f"Fetching details for form UID: {first_form_uid}...")
        
        form_details = kobo_client.get_form_details(first_form_uid)
        
        output_filename = "form_structure.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(form_details, f, indent=2, ensure_ascii=False)
            
        print(f"\nSuccessfully saved form structure to '{output_filename}'.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    debug_kobo_form_structure()