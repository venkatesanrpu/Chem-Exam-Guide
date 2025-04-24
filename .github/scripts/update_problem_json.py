import os
import json
import sys
from pathlib import Path

def load_json(file_path):
    print(f"DEBUG: Loading JSON from {file_path}")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                print(f"DEBUG: Successfully loaded JSON: {data}")
                return data
            except json.JSONDecodeError:
                print(f"DEBUG: JSON decode error, initializing empty list")
                return []
    print(f"DEBUG: JSON file does not exist, initializing empty list")
    return []

def save_json(file_path, data):
    print(f"DEBUG: Saving JSON to {file_path}")
    print(f"DEBUG: Data to save: {json.dumps(data, indent=2)}")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"DEBUG: Successfully saved JSON to {file_path}")

def process_image_file(image_path, github_repo):
    print(f"DEBUG: Processing image: {image_path}")
    path_parts = Path(image_path).parts
    print(f"DEBUG: Path parts: {path_parts}")
    
    # Handle paths like: addition_reaction/images/alkene_addition/image.png
    # or problem-set-1/images/difficult/image.png
    if len(path_parts) < 4 or path_parts[-3] != 'images':
        print(f"DEBUG: Skipping invalid path structure: {image_path}")
        return None
    
    problem_folder = path_parts[-4]  # e.g., addition_reaction or problem-set-1
    level_or_reaction = path_parts[-2]  # e.g., alkene_addition or difficult
    image_name = path_parts[-1]      # e.g., image.png
    
    # Extract repository owner and repo name
    repo_owner = github_repo.split('/')[0]
    repo_name = github_repo.split('/')[1]
    
    # Construct URL with images/level_or_reaction
    question_url = f"https://{repo_owner}.github.io/{repo_name}/{problem_folder}/images/{level_or_reaction}/{image_name}"
    
    entry = {
        "question_url": question_url,
        "question_level": level_or_reaction,  # e.g., alkene_addition or difficult
        "question_category": level_or_reaction,
        "question_text": "Solve the problem ..."
    }
    
    print(f"DEBUG: Created entry: {entry}")
    return problem_folder, level_or_reaction, entry

def main():
    changed_files = os.getenv('CHANGED_FILES', '').split('\n')
    github_repo = os.getenv('GITHUB_REPOSITORY', '')
    
    print(f"DEBUG: Changed files: {changed_files}")
    print(f"DEBUG: GitHub repository: {github_repo}")
    
    json_updates = {}
    
    for file in changed_files:
        if not file or not file.lower().endswith(('.png', '.gif', '.jpg', '.svg')):
            print(f"DEBUG: Skipping non-image file: {file}")
            continue
            
        # Normalize path for manual runs (remove leading './' from find command)
        file = file.lstrip('./')
        
        result = process_image_file(file, github_repo)
        if result:
            problem_folder, level_or_reaction, entry = result
            json_file = f"{problem_folder}/{level_or_reaction}.json"
            print(f"DEBUG: Targeting JSON file: {json_file}")
            if json_file not in json_updates:
                json_updates[json_file] = load_json(json_file)
            
            # Check if entry already exists to avoid duplicates
            if not any(e['question_url'] == entry['question_url'] for e in json_updates[json_file]):
                json_updates[json_file].append(entry)
                print(f"DEBUG: Added new entry to {json_file}")
            else:
                print(f"DEBUG: Entry already exists in {json_file}, skipping")
    
    for json_file, data in json_updates.items():
        print(f"DEBUG: Updating JSON file: {json_file}")
        if data:  # Only save non-empty JSON files
            save_json(json_file, data)
        else:
            print(f"DEBUG: Skipping empty JSON file: {json_file}")

if __name__ == "__main__":
    print("DEBUG: Starting script execution")
    try:
        main()
        print("DEBUG: Script completed successfully")
    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        sys.exit(1)
