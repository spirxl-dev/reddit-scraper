import os
import json
import argparse

def validate_json_files(folder_path):
    total_files = 0
    valid_files = 0
    invalid_files = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            total_files += 1
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"{filename}: Valid JSON")
                valid_files += 1
            except json.JSONDecodeError as e:
                print(f"{filename}: Invalid JSON - {str(e)}")
                invalid_files += 1
            except Exception as e:
                print(f"{filename}: Error - {str(e)}")
                invalid_files += 1

    print(f"Valid JSON files: {valid_files}")
    print(f"Invalid JSON files: {invalid_files}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate JSON files in a folder.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing JSON files.')
    args = parser.parse_args()

    validate_json_files(args.folder_path)