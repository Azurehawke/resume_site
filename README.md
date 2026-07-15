# resume_site

An interactive, self-hosted resume site with a private editing portal and
unlimited employer/position-targeted public pages.

- **Private portal** (login required): enter your profile, contact info, and
  resume content once — employment history, education, skills, or any other
  section you define — using a rich-text editor.
- **Target pages**: for each job application, create a page and check off
  exactly which sections, entries, and individual bullets to show. Each page
  gets its own private, unguessable link (`/r/<token>/`) to put on that
  employer's resume.
- **Public page**: header with your photo, name and contact info, and
  expandable cards for each section — click the `+` to reveal duties,
  courses, or other detail bullets.
- **PDF export**: download a PDF of any target page's resume from the
  portal.
- **Analytics**: per-page view counts and a recent-visits log (your own
  logged-in visits aren't counted).

## Content model

- **Section** — a top-level heading (Employment History, Education, Skills,
  or any section you add). Has a layout: `timeline` (dated entries with
  expandable bullets), `skills` (categories of tags), or `text` (a plain
  rich-text block).
- **Entry** — one card within a section: a job, a degree, or a skill
  category. Has a heading, subheading, location, date range, and a one-line
  summary that's visible even when collapsed.
- **DetailItem** — one bullet under an entry: a job duty, a course, or a
  single skill tag.
- **PublicPage** — one employer-targeted page. Selects which sections,
  entries, and detail items to show via checkboxes in the portal.

Manage Section/Entry/DetailItem/Profile content at `/django-admin/` (linked
from the portal dashboard); manage target pages and their checkbox
selections at `/pages/`.

## Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export APP_DATA_DIR=./data   # keeps sqlite db + uploaded media out of the repo
mkdir -p data/media

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/login/` to log into the portal, or
`/django-admin/` directly.

## Deploying with Docker (behind Cloudflare Tunnel)

This follows the same pattern as other self-hosted services: a Docker
container bound to your internal network address, with `cloudflared` (run
separately, same as your other tunnels) pointing its ingress at this
container.

```bash
cp .env.example .env
# edit .env: set DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS

docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

The container listens on `100.107.227.53:9130` (mapped from its internal
port 8000). Point your Cloudflare Tunnel's ingress rule for this hostname at
`http://100.107.227.53:9130`.

Data persists in the `resume_data` Docker volume (SQLite database + uploaded
media, including your profile photo), so it survives image rebuilds.

### First-time setup after deploying

1. Log in at `/login/`, or go straight to `/django-admin/`.
2. Add your **Profile** (name, contact info, photo, optional summary) and
   any **ProfileLinks** (LinkedIn, GitHub, etc).
3. Add **Sections** (e.g. Employment History, Education, Skills), then their
   **Entries** and **DetailItems** — this is where the rich-text editor is
   used for job duties, course descriptions, etc.
4. Go to `/pages/new/` to create your first target page, then check off
   what it should show.
5. Copy the private link shown on the target page's edit screen and put it
   on the resume you send to that employer.

## Notes

- Target-page links are unguessable tokens rather than readable slugs —
  treat the link itself as the access control. Toggling "Published" off on
  a page makes it 404 for the public while remaining visible to you when
  logged in (handy for staging a page before sending it out).
- The public page and PDF export always reflect exactly what's checked off
  for that target page — nothing else leaks through.
