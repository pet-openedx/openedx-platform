# Local Development Usage

## 1. Start backing services (once per machine restart)
```bash
make run-services
```
Starts MySQL (3306), MongoDB (27017), Redis (6380) in Docker with ports exposed.

## 2. Run the servers (separate terminals)
```bash
make run-lms   # http://localhost:8000
make run-cms   # http://localhost:8001
```

## 3. Access the apps

| App | URL | Purpose |
|-----|-----|---------|
| LMS | http://localhost:8000 | Learner-facing platform |
| CMS (Studio) | http://localhost:8001 | Course authoring |
| LMS Admin | http://localhost:8000/admin | Django admin |
| LMS API | http://localhost:8000/api/ | REST APIs |
| Heartbeat | http://localhost:8000/heartbeat | Health check |

## 4. Log in

Create a superuser (one-time):
```bash
LMS_CFG="/Users/viveksingh/Library/Application Support/tutor/env/apps/openedx/config/lms.env.yml" \
python manage.py lms createsuperuser
```
Then log in at http://localhost:8000/login or http://localhost:8000/admin.

## 5. Frontend pages need webpack (optional)

The HTML pages (login, dashboard, etc.) require compiled assets:
```bash
npm run build-dev    # one-time build
# or during active JS development:
npm run watch        # rebuilds on file changes
```
Without this, HTML pages return 500. REST APIs work without it.

## 6. MFE development

If working on a MFE (e.g. `frontend-app-learning` on `localhost:2000`), the LMS API is
already configured to allow it. Point your MFE's `.env.development` at `http://localhost:8000`.

## 7. Database migrations (after pulling new code)
```bash
make migrate-lms
make migrate-cms
```

## First-time setup

```bash
make macos-requirements   # install brew deps (once)
make dev-requirements     # install Python deps
npm install               # install Node deps
make migrate-lms          # run DB migrations
make migrate-cms
```
