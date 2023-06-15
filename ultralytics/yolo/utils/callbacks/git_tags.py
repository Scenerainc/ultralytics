"""in this file we have the simple function

```python
repository_tags(*args, **kwargs) -> dict[str, str]
```

please take a look at it's docstring for usage

Motivation
----------

We at Scenera log our training runs with specific tags to keep track of the source used to train

```json
{
    "git-branch": "add_mlflow",
    "git-hash": "8077f7c47bc1ccc592187374a4bd5c967483910b",
    "git-origin": "git@github.com:YoRigid/scenera-yolov5.git",
    "git-submodule-yolov5-branch": "master",
    "git-submodule-yolov5-hash": "6e04b94fa9fb12ff66b2329660de8a5a8e5f1b1d",
    "git-submodule-yolov5-origin": "https://github.com/ultralytics/yolov5"
}
```

```dirtree

mlruns/0/38b29ac01a244cf6b7bee13934b285cb/params
├── artifact_alias
├── batch_size
├── bbox_interval
├── cos_lr
├── data
├── epochs
├── exist_ok
├── freeze
├── git-branch                    <---
├── git-hash                      <---
├── git-origin                    <---
├── git-submodule-yolov5-branch   <---
├── git-submodule-yolov5-hexsha   <---
├── git-submodule-yolov5-origin   <---
|
```
"""

from __future__ import annotations
from git import Repo


class DirtyGitRepo(BaseException):
    """Repository has modified files"""


def repository_tags(
    prefix: str = "git", search_parent_directories: bool = False, suppress: bool = False
) -> dict[str, str]:
    """Git repository tags

    Fetch git information from current context

    Parameters
    ----------
    prefix : str, optional
        parameter prefix, by default "git"
    search_parent_directories: bool, optional
        search parent dirs for git repository, by default 'False',
    suppress: bool, optional
        suppress uncommitted changes check, by default 'False'

    Returns
    -------
    dict[str, str]
        current git repository information

    Raises
    ------
    DirtyGitRepo:
        Unstashed changes to the repository or submodule (don't make changes to the submodule)
    InvalidGitRepositoryError:
        GitPython Error, repository is not found
    NoSuchPathError:
        GitPython Error, repository is not found

    Example
    -------

    >>> import json
    >>> from git_utils import repository_tags()
    >>> json.dumps(repository_tags(prefix="git"))

    ```json
    {
        "git-branch": "add_mlflow",
        "git-hash": "8077f7c47bc1ccc592187374a4bd5c967483910b",
        "git-origin": "git@github.com:YoRigid/scenera-yolov5.git",
        "git-submodule-yolov5-branch": "master",
        "git-submodule-yolov5-hash": "6e04b94fa9fb12ff66b2329660de8a5a8e5f1b1d",
        "git-submodule-yolov5-origin": "https://github.com/ultralytics/yolov5"
    }
    ```

    """

    repo = Repo(search_parent_directories=search_parent_directories)
    if repo.is_dirty(untracked_files=True, submodules=True) and not suppress:
        raise DirtyGitRepo(
            "The purpose of logging git tags is being able to repoduce. \
            \n Please commit and push OR restore your changes"
        )
    prefix = prefix or "git"
    data = {
        f"{prefix}-branch": repo.active_branch,
        f"{prefix}-hash": repo.head.object.hexsha,
        f"{prefix}-origin": repo.remotes.origin.url,
    }
    for submodule in repo.submodules:
        _prefix = f"{prefix}-submodule-{submodule.name}"
        data.update(
            {
                f"{_prefix}-branch": submodule.branch,
                f"{_prefix}-hash": submodule.hexsha,
                f"{_prefix}-origin": submodule.url,
            }
        )

    return {key: str(val) for key, val in data.items()}