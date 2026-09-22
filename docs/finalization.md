# Screenshots and PR preparation

## Prepare sample data

Run migrations, create a superuser, and authenticate in Swagger with its access
token or sign in to the Browsable API at `/api-auth/login/`.
Create two airports, a route, an aircraft type, an aircraft, crew members, and
a flight. Register a regular user and place an order.
Use `?page_size=1` to demonstrate pagination.

## Screenshot checklist

- [ ] `/api/docs/`: title, endpoint groups, and the Authorize button.
- [ ] Swagger GET `/api/airport/flights/`: source/destination/date/page parameters,
  an executed request, and a 200 response with count/results/tickets_available.
- [ ] `/api/airport/flights/<id>/`: detail with route, aircraft, crew, and taken_seats.
- [ ] `/api/airport/routes/`: filtered list, and `/api/airport/routes/<id>/`: detail.
- [ ] As staff: POST forms for `/api/airport/airports/` and `/api/airport/flights/`.
- [ ] As staff: airport detail with a PUT/PATCH form and DELETE available.
- [ ] Registration at `/api/user/register/` and token retrieval at `/api/user/token/`:
  email/password fields and successful status, with passwords and token values hidden.
- [ ] GET `/api/user/me/`: Bearer authentication; use a sample email address.
- [ ] POST `/api/airport/orders/`: tickets JSON and a 201 response. Enter the nested
  list in Swagger or the Browsable API's Raw data form.
- [ ] GET `/api/airport/orders/`: orders belonging to the current user.
- [ ] As a regular user: attempting to POST an airport returns 403.
- [ ] Optional: invalid date → 400; exceeding the POST orders limit → 429;
  `/api/redoc/` with an expanded schema.
- [ ] Export draw.io to `docs/images/database.png`; save the source as `docs/database.drawio`.

Save images under `docs/images/` and add Markdown links to the PR description.
The diagram export and screenshots still need to be created manually;
this checklist does not imply that those images already exist.

## Check the branch and changes

Run these commands from the project root. The intended working branch is develop.

```powershell
git status --short
git branch --show-current
git remote -v
git fetch origin
git log --oneline origin/main..develop
git diff --stat origin/main...develop
```

If you are on another branch, first save uncommitted changes with
`git stash push -u -m "airport finalization"`, then run `git switch develop`
and `git stash pop`. Resolve any conflicts before continuing.
Transfer needed commits from another branch with `git cherry-pick <commit-sha>`;
switching to develop does not transfer those commits automatically.

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py spectacular --file schema.yaml --validate --fail-on-warn
git diff --check
git diff
git ls-files --others --exclude-standard
```

## Final commits

A single commit can capture the current set of related changes:

```powershell
git add airport airport_service user requirements.txt requirements-runtime.txt README.md docs schema.yaml Dockerfile compose.yaml .dockerignore
git diff --cached --stat
git diff --cached
git commit -m "feat: finalize airport API and add Docker support"
git status --short
```

This also stages previously uncommitted user application files; review the
staged diff. Do not add .env, db.sqlite3, or .venv.
If splitting changes into independent commits with `git add -p`, possible titles are:

- `fix: support email user creation and protect private orders`
- `feat: add staff permissions, pagination, filters and order throttling`
- `docs: add OpenAPI, setup guide and database structure`
- `build: add Docker Compose setup with persistent PostgreSQL storage`
- `test: cover authentication and airport API access rules`

For the documentation translation alone:

```text
docs: translate README and project guides into English
```

After manually adding the images:

```powershell
git add docs
git commit -m "docs: add database diagram and API screenshots"
git push -u origin develop
```

If the push is rejected because the remote has new commits, run `git fetch origin`,
inspect `git log --oneline --left-right develop...origin/develop`, merge the
changes with `git merge origin/develop`, resolve conflicts, and repeat the checks.
This workflow does not require a force push.

## Create a develop → main PR

On GitHub, select Pull requests → New pull request → **base: main**, **compare: develop**.
Review Files changed, paste the text from [pr-description.md](pr-description.md),
attach the images, and click Create pull request.

If GitHub CLI is installed and authenticated:

```powershell
gh pr create --base main --head develop --title "Finalize Airport Service API" --body-file docs/pr-description.md
```

Update the PR checklist to reflect actual results before publishing.
Merge after review and successful checks.
