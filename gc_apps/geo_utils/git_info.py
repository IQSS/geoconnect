"""
Convenience methods to display branch information on the web page
"""
from __future__ import print_function
from git import Repo, NoSuchPathError, InvalidGitRepositoryError

import logging
from django.conf import settings

LOGGER = logging.getLogger(__name__)

def get_branch_info():
    """Return the information about this git branch.
    If no branch is present, return an empty dit
    """
    try:
        repo = Repo(settings.SITE_ROOT)
    except (NoSuchPathError, InvalidGitRepositoryError) as ex_obj:
        LOGGER.error('error: %s', ex_obj)
        return {}

    repo_commit = repo.commit()
    if not repo_commit:
        return {}

    return dict(git_active_branch=repo.active_branch.name,
                git_hexsha=repo_commit.hexsha,
                git_hexsha_short=repo_commit.hexsha[:7])
