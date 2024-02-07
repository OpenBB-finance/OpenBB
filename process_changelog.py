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

    pr_occurrences = {}

    # First pass: Collect all occurrences of PR numbers
    for i, line in enumerate(lines):
        match = re.search(r'\(#(\d+)\)', line)
        if match:
            pr_number = int(match.group(1))
            if pr_number not in pr_occurrences:
                pr_occurrences[pr_number] = []
            pr_occurrences[pr_number].append(i)

    # Determine lines to remove: all but the last occurrence for each PR number
    to_remove = {i for pr, indices in pr_occurrences.items() if len(indices) > 1 for i in indices[:-1]}
    # Remove entries for PR numbers less than or equal to release_pr_number
    to_remove.update(i for pr, indices in pr_occurrences.items() for i in indices if pr <= release_pr_number)

    processed_lines = [line for i, line in enumerate(lines) if i not in to_remove]

    # Final sweep: Check for any missed duplicates
    final_lines = []
    seen_pr_numbers = set()
    for line in reversed(processed_lines):  # Reverse to start from the last occurrence
        match = re.search(r'\(#(\d+)\)', line)
        if match:
            pr_number = int(match.group(1))
            if pr_number in seen_pr_numbers:
                # If we've seen this PR number, it's a duplicate; skip it
                continue
            seen_pr_numbers.add(pr_number)
        final_lines.append(line)
    final_lines.reverse()  # Reverse back to original order

    try:
        with open(file_path, 'w') as file:
            file.writelines(final_lines)
    except IOError as e:
        print(f"Failed to write to file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_changelog.py <changelog_file> <release_pr_number>")
        sys.exit(1)

    file_path = sys.argv[1]
    release_pr_number = int(sys.argv[2])
    process_changelog(file_path, release_pr_number)
