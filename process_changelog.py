# process_changelog.py
import re
import sys

def process_changelog(file_path, release_pr_number):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except IOError as e:
        print(f"Failed to open or read file: {e}")
        return

    to_remove = set()
    pr_dict = {}

    for i, line in enumerate(lines):
        match = re.search(r'\(#(\d+)\)', line)
        if match:
            pr_number = int(match.group(1))
            if pr_number <= release_pr_number:
                to_remove.add(i)
            else:
                pr_dict[pr_number] = line

    processed_lines = [line for i, line in enumerate(lines) if i not in to_remove]

    try:
        with open(file_path, 'w') as file:
            file.writelines(processed_lines)
    except IOError as e:
        print(f"Failed to write to file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_changelog.py <changelog_file> <release_pr_number>")
        sys.exit(1)

    file_path = sys.argv[1]
    release_pr_number = int(sys.argv[2])
    process_changelog(file_path, release_pr_number)
