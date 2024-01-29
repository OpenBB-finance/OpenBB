def process_changelog(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    release_pr_number = None
    pr_dict = {}
    to_remove = set()

    # Identify the latest release PR number
    for line in lines:
        if line.startswith('* Release/') and '(#' in line:
            release_pr_number = int(line.split('(#')[1].split(')')[0])
            break

    if release_pr_number is None:
        print("No release PR found. Exiting.")
        return

    # Process PRs, keeping only those larger than the release PR number
    for i, line in enumerate(lines):
        if line.startswith('*') and '(#' in line:
            pr_number = int(line.split('(#')[1].split(')')[0])
            if pr_number <= release_pr_number:
                to_remove.add(i)
            elif pr_number in pr_dict:
                to_remove.add(i)
            else:
                pr_dict[pr_number] = i

    processed_lines = [line for i, line in enumerate(lines) if i not in to_remove]

    with open(file_path, 'w') as file:
        file.writelines(processed_lines)

# Replace 'path_to_your_changelog.md' with your actual file path
process_changelog('test.md')