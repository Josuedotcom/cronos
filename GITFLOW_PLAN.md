# GitFlow Setup Plan for Cronos

## Current State
- ✅ Main branch with 5 commits (SDD planning done)
- ❌ No develop branch
- ❌ No feature branches
- ❌ Backend code not committed (untracked)
- ❌ design.md, tasks.md not committed

## GitFlow Structure to Implement

```
main (stable releases only)
  └── develop (integration branch)
       ├── feature/sdd-init (merged)
       ├── feature/backend-sprint-1-1 (IN PROGRESS - current)
       └── feature/... (future features)
```

## Plan

### Step 1: Create develop branch from main
```bash
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

### Step 2: Create feature branch for Sprint 1.1
```bash
git checkout develop
git checkout -b feature/backend-sprint-1-1
```

### Step 3: Add untracked files to feature branch
```bash
git add backend/
git add openspec/changes/cronos-mvp/design.md
git add openspec/changes/cronos-mvp/tasks.md
git commit -m "feat: Sprint 1.1 - FastAPI scaffold, ORM models, Alembic migrations"
git push -u origin feature/backend-sprint-1-1
```

### Step 4: Create Pull Request (feature → develop)
```bash
gh pr create \
  --base develop \
  --head feature/backend-sprint-1-1 \
  --title "Sprint 1.1: Backend Foundation (FastAPI, ORM, Migrations)" \
  --body "..."
```

### Step 5: After approval/testing, merge to develop
```bash
git checkout develop
git merge feature/backend-sprint-1-1
git push origin develop
```

### Step 6: After all sprints done, release to main
```bash
git checkout main
git merge --no-ff develop
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags
```

## Protection Rules to Set in GitHub

### main branch:
- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass
- ✅ Restrict who can push (project owner only)
- ✅ No force pushes

### develop branch:
- ✅ Require pull request reviews (1 approval)
- ✅ Auto-delete head branches

## Branch Naming Convention
- `feature/xxx` - New features (max 1-2 sprints)
- `bugfix/xxx` - Bug fixes
- `hotfix/xxx` - Critical fixes to main
- `release/v1.0.0` - Release preparation branch

## Commit Message Convention (Conventional Commits)
- `feat: Add feature description`
- `fix: Fix bug description`
- `docs: Update documentation`
- `refactor: Refactor code`
- `test: Add tests`
- `chore: Update dependencies`
- `sdd: SDD phase updates`
