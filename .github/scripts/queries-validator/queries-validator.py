import os
import requests
import json
from pathlib import Path
from jsonschema import validate

KICS_PR_NUMBER = os.getenv('KICS_PR_NUMBER')
KICS_GITHUB_TOKEN = os.getenv('KICS_GITHUB_TOKEN')
QUERIES_PATH = 'assets/queries'
QUERIES_METADATA = 'metadata.json'

def exit_with_error(message):
    print(message)
    exit(1)

def exit_success():
    print('Successfully execution!')
    exit(0)

def fetch(page=1, max_items=100):
    print(f'Fetching PR #{KICS_PR_NUMBER} files... #page{page}')
    headers = {'Authorization': f'token {KICS_GITHUB_TOKEN}'}
    url = f'https://api.github.com/repos/checkmarx/kics/pulls/{KICS_PR_NUMBER}/files?per_page={max_items}page={page}'

    response = requests.get(url, headers=headers)
    return { "data": response.json(), "status": response.status_code }

def fetch_pr_files():
    files = []
    max_items = 100

    for page in range(1, 50):
        response = fetch(page, max_items)
        if response['status'] != 200:
            return exit_with_error(
                f"Failed to fetch PR files\n- status code: {response['status']}"
            )


        files.extend(
            obj['filename']
            for obj in response['data']
            if obj['status'] != 'removed'
        )

        if len(response['data']) < max_items:
            return files

    return exit_with_error('Failed to fetch PR files\n- too many pages')

def find_queries_in_files(files):
    return [
        file
        for file in files
        if file.endswith(QUERIES_METADATA) and file.startswith(QUERIES_PATH)
    ]

def validate_queries_metadata(queries):
    errors = []

    with open('metadata-schema.json') as fileSchema:
        schema = json.load(fileSchema)
        for i, query in enumerate(queries):
            print(f'[{i}] Validating "{query}" ...')

            complete_path = os.path.abspath(os.path.join('..', '..', '..', Path(query)))

            with open(complete_path) as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    errors.append(f'Failed to parse {query}')
                try:
                    validate(instance=data, schema=schema)
                except Exception as e:
                    errors.append(f'Failed to validate {query}: {e}')

    if errors:
        for error in errors:
            print(error)
        exit_with_error(f'There are metadata files with errors ({len(errors)} files)')

def fetch_all_metadata_files():
    complete_path = os.path.abspath(os.path.join('..', '..', '..', 'assets', 'queries'))

    queries_list = []
    for root, _, files in os.walk(complete_path):
        queries_list.extend(
            os.path.join(root, file)
            for file in files
            if file.endswith(QUERIES_METADATA)
        )

    return queries_list

def validate_all_queries():
    queries_list = fetch_all_metadata_files()
    validate_queries_metadata(queries_list)
    exit_success()

def validate_pr_queries():
    changed_files = fetch_pr_files()
    queries = find_queries_in_files(changed_files)
    validate_queries_metadata(queries)
    exit_success()

if __name__ == '__main__':
    validate_pr_queries()
    #validate_all_queries()
