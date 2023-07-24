# IMPORT STANDARD
from pathlib import Path

import requests

# IMPORT THIRD-PARTY
# IMPORT INTERNAL

try:
    import git
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True

GITHUB_PROJECT_URL = (
    "https://api.github.com/repos/openbb-finance/openbbterminal/branches"
)

UNKNOWN_COMMIT_PLACEHOLDER = "unknown-commit"
UNKNOWN_BRANCH_PLACEHOLDER = "unknown-branch"
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent.parent


def get_commit_hash() -> str:
    """Get Commit Short Hash"""

    git_dir = REPOSITORY_DIRECTORY.joinpath(".git")

    if WITH_GIT and git_dir.is_dir():
        repo = git.Repo(path=git_dir)
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=8)
        commit_hash = f"sha:{short_sha}"
    else:
        commit_hash = UNKNOWN_COMMIT_PLACEHOLDER

    return commit_hash


def get_branch(commit_hash: str, request_timeout: int = 5) -> str:
    """Get Branch Name"""

    def get_branch_commit_hash(branch: str) -> str:
        response = requests.get(
            f"{GITHUB_PROJECT_URL}/{branch}", timeout=request_timeout
        )
        return "sha:" + response.json()["commit"]["sha"][:8]

    for branch in ["main", "develop"]:
        try:
            if get_branch_commit_hash(branch) == commit_hash:
                return branch
        except Exception:
            pass

    git_dir = REPOSITORY_DIRECTORY.joinpath(".git")
    if WITH_GIT and git_dir.is_dir():
        try:
            repo = git.Repo(path=git_dir)
            branch = repo.active_branch.name
            return branch
        except Exception:
            pass

    return UNKNOWN_BRANCH_PLACEHOLDER
