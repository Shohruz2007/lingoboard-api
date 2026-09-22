# LingoBoard API

Backend for a language-learning platform: teachers publish assessments and
lesson material, students sit them, and the service grades the result and
tracks progress over time.

Django REST Framework, PostgreSQL, Redis and Celery.

## What it does

- **Assessments** built from sections (`AssessmentSection`), each holding its
  content and answer key as JSON, so a new exam format needs no migration.
- **Grading** dispatched through a registry (`assessment/service/grading/`):
  reading, listening, vocabulary and grammar are scored by comparison against
  the answer key; writing goes to an LLM prompted with the band criteria in
  `utils/writing_grade_criteria.txt`. Unknown types fall back to a no-op grader
  rather than failing.
- **Mock exams** that chain sections into a full sitting, with progress and
  per-section status tracked separately from results.
- **Material** — lessons and downloadable files, ordered and paginated.

## Layout

Each app separates the layers rather than piling everything into `views.py`:

```
assessment/
  api/          DRF views, split by audience (admin / student / assessment)
  domain/       models, constants, exceptions
  selector/     read queries
  service/      write paths and grading
  serializer/   one module per resource
```

## Running it

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env        # fill in SECRET_KEY, DATABASE_URL, OPENAI_KEY
python manage.py migrate
python manage.py runserver
```

`PERFORMANCE_OPTIMIZATION.md` documents the indexes, `select_related` /
`prefetch_related` passes and Redis caching added to cut N+1 queries.

## Note on history

This repository is a clean-history export of a private working repo. The
original carried build artifacts and an accidentally committed upload; the
code here is the same, minus that baggage.
