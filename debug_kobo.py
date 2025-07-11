import os
import pandas as pd
from dotenv import load_dotenv
from Kobo.kobo_toolbox_client import KoboToolboxClient
import sys

# Force stdout to UTF-8 for consistent output, especially on Windows
sys.stdout.reconfigure(encoding='utf-8')

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
        
        # Get raw data
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
        
        # Add prints inside the _get_submissions_with_options logic
        # To do this, I need to replicate part of _get_submissions_with_options here
        # This is a temporary measure for debugging.
        results = raw_data_response.get('results', [])
        if results:
            asset = kobo_client.kobo.get_asset(first_form_uid)
            choice_lists = kobo_client.kobo.get_choices(asset).get('choices', {})
            questions = kobo_client.kobo.get_questions(asset, unpack_multiples=True)

            print("\n--- DEBUGGING: Sample Labeled and Flattened Result ---")
            sample_raw_result = results[0]
            print("Sample Raw Result:", sample_raw_result)

            sample_labeled_result = kobo_client.kobo.label_result(
                unlabeled_result=sample_raw_result,
                choice_lists=choice_lists,
                questions=questions,
                unpack_multiples=True
            )
            print("Sample Labeled Result from koboextractor.label_result:", sample_labeled_result)

            # Call the actual _flatten_and_label_submission method from the client instance
            # Temporarily add choice_lists and questions to the client for this debug run if needed by _flatten_and_label_submission
            # (It shouldn't be needed after my last change, but good to be aware)
            # Re-reading kobo_toolbox_client.py to confirm _flatten_and_label_submission signature
            # It currently takes only labeled_result
            sample_flat_labeled_result = kobo_client._flatten_and_label_submission(sample_labeled_result)
            print("Sample Flattened Labeled Result from _flatten_and_label_submission:", sample_flat_labeled_result)
            print("--- END DEBUGGING ---\n")

        # Attempt to get submissions and print head
        submissions_df = kobo_client.get_submissions(first_form_uid)
        print("Submissions DataFrame Head:\n", submissions_df.head())

    else:
        print("No forms found.")
except Exception as e:
    print(f'\nError occurred while fetching submissions: {e}')