# Git Workflows

Git is a distributed version control system. Commits form a directed history;
branches are movable pointers to commits.

## Everyday commands
- `git status` — working tree state.
- `git switch -c feature/x` — create and switch to a branch.
- `git add -p` — stage changes interactively, hunk by hunk.
- `git commit -m "message"` — record staged changes.
- `git push -u origin feature/x` — publish a branch.
- `git log --oneline --graph --decorate` — compact history view.

## Branching models
- **Trunk-based**: short-lived branches merged frequently into `main`; pairs well
  with CI and feature flags.
- **Git Flow**: long-lived `develop`/`release`/`hotfix` branches; heavier, suited
  to scheduled releases.

## Undoing things safely
- Discard unstaged changes to a file: `git restore <file>`.
- Unstage a file: `git restore --staged <file>`.
- Revert a pushed commit (creates a new inverse commit): `git revert <sha>`.
- Move the branch pointer back, keeping changes: `git reset --soft <sha>`.
- `git reset --hard` discards work permanently — use with care.

## Merge vs rebase
- **Merge** preserves history and creates a merge commit.
- **Rebase** replays your commits on top of another branch for a linear history.
  Never rebase commits that others have already pulled.

## Pull requests
- Keep PRs small and focused; write a clear description of what and why.
- Require review + green CI before merging.
- Squash-merge to keep `main` history tidy when commits are noisy.
