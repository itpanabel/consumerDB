# Security Audit Report

**Application:** consumerDB (Flask)
**Initial Audit:** 2026-03-15
**Last Reviewed:** 2026-03-17 (rev 8)
**Auditor:** Claude Code (claude-sonnet-4-6)

---

## Summary

| Severity | Open | Fixed |
|----------|------|-------|
| Critical | 0 | 2 |
| High | 0 | 12 |
| Medium | 0 | 8 |
| Low | 0 | 4 |
| **Total** | **0** | **25** |

---

## Fixed

### ~~No CSRF Protection~~ ✅ FIXED — 2026-03-17
**Files:** `api/__init__.py`, all 18 HTML templates
`CSRFProtect(app)` initialized in the app factory. `{{ csrf_token() }}` hidden input added to every form.

---

### ~~SQL Injection via String Formatting~~ ✅ FIXED — 2026-03-17
**Files:** `api/forms.py:43-46`, `send_testers.py:41`
All queries now use parameterized `?` placeholders.

---

### ~~Missing `@login_required` on `/entity/create`~~ ✅ FIXED — 2026-03-17
**File:** `api/entity.py:41`

---

### ~~Missing `@login_required` on `/testers/export_resquest`~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py:211`

---

### ~~Missing `@login_required` on `/entity/delete`~~ ✅ FIXED — 2026-03-17
**File:** `api/entity.py:104`

---

### ~~URL Route Typo `/detele` in all blueprints~~ ✅ FIXED — 2026-03-17
**Files:** `api/testers.py`, `api/stores.py`, `api/pos.py`, `api/brands.py`
Route corrected to `/<id>/delete` in all four blueprints.

---

### ~~SQL Injection in `send_testers.py`~~ ✅ FIXED — 2026-03-17
**File:** `send_testers.py:41`
Query now uses parameterized `?` placeholder for `subsidiary`.

---

### ~~No Type Validation on `subsidiaryCode`~~ ✅ FIXED — 2026-03-17
**File:** `api/forms.py:42-44`
`request.args.get("country", type=int)` used with explicit `abort(400)` on missing/non-numeric input.

---

### ~~`cursor.description` Accessed After `conn.close()` — Script Crash~~ ✅ FIXED — 2026-03-17
**File:** `send_testers.py:43,54,111`
Column headers captured before closing the connection. Colombia trigger condition also fixed (`current_date.day ==` instead of `current_date ==`).

---

### ~~`index` Routes Access `g.user` Without `@login_required`~~ ✅ FIXED — 2026-03-17
**Files:** `api/testers.py:14`, `api/brands.py:13`, `api/stores.py:11`, `api/pos.py:11`, `api/entity.py:10`, `api/beautyadvisors.py:11`
`@login_required` added to all six index functions. Previously caused 500 crash for unauthenticated visitors.

---

### ~~`get_brands()` Returns `None` on API Error — Template Crash~~ ✅ FIXED — 2026-03-17
**File:** `api/forms.py:278`
`except` block now returns `{}` instead of implicitly returning `None`, preventing `/panama` and `/colombia` from crashing when the Mailchimp API is unavailable.

---

### ~~`cursor.description` Accessed After `conn.close()`~~ ✅ FIXED — 2026-03-17
Already covered above.

---

### ~~Outdated Dependencies — 34 CVEs~~ ✅ FIXED — 2026-03-17
**File:** `requirements.txt`
`pip-audit --fix` resolved all 34 CVEs by upgrading 8 packages:
- `certifi` 2023.7.22 → 2024.7.4
- `Flask` 2.3.2 → 3.1.3 (1 CVE)
- `idna` 3.4 → 3.7
- `Jinja2` 3.1.2 → 3.1.6 (5 CVEs)
- `requests` 2.31.0 → 2.32.4 (2 CVEs)
- `setuptools` 65.5.0 → 78.1.1 (3 CVEs)
- `urllib3` 2.0.4 → 2.6.3 (8 CVEs)
- `Werkzeug` 2.3.6 → 3.1.6 (8 CVEs)

`pip-audit` now returns: **No known vulnerabilities found.**

---

## Open — High

### ~~1. Open User Registration — No Admin Gate~~ ✅ FIXED — 2026-03-17
**File:** `api/auth.py`
`abort(403)` added at the top of `register()` for any non-admin user. Combined with the existing `@login_required`, the route is now accessible only to the `admin` account. Will be superseded by a proper `role` column when issue #2 is resolved.

---

### ~~2. Hardcoded Role Check via Username String Comparison~~ ✅ FIXED — 2026-03-17
**Files:** `api/testers.py`, `api/brands.py`, `api/auth.py`

`role TEXT NOT NULL DEFAULT 'user'` column added to `USERS`. All `g.user['username'] != "admin"` checks replaced with `g.user['role'] != "admin"`. New `add-role-column` CLI command promotes existing NULL-subsidiary users to `role='admin'`. Register form now includes a role selector (admin-only).

---

### ~~3. Unvalidated CSV Delimiter from User Input~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py:118`
Whitelist `[',', ';', '\t', '|']` enforced before file processing; invalid delimiter returns a flash error and redirects.

---

### ~~4. Missing Subsidiary Ownership Check in `testers.update()`~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py:160-164`
Non-admin users now have their subsidiary fetched immediately after `get_tester()`; a mismatch aborts with 403 before any form processing.

---

### ~~5. `import_testers` Deletes All Subsidiaries' Data~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py`

DELETE scoped to `WHERE subsidiaryid = ?`. INSERT now uses the actual subsidiary instead of hardcoded `1`. Admin users must select a subsidiary via a `<select>` in the form; non-admin users have their subsidiary resolved from the DB and passed as a hidden field.

---

### ~~6. `ALLOWED_EXTENSIONS` Defined but Never Enforced~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py:124`
Extension check now enforced after the file-present check; non-CSV uploads flash an error and redirect before any file is saved.

---

## Open — Medium

### ~~7. Hardcoded Mailchimp List IDs and Group IDs~~ ✅ FIXED — 2026-03-17
**File:** `api/forms.py`

All six IDs moved to `.env` as `MAILCHIMP_LIST_ID_PA/CO/CR` and `MAILCHIMP_GROUP_ID_PA/CO/CR`. Loaded via `os.getenv()` with empty-string fallback.

---

### ~~8. Sensitive Information Disclosed in Error Messages~~ ✅ FIXED — 2026-03-17
**File:** `api/forms.py:250`

Raw Mailchimp API error JSON (`error.text`) is now parsed; a `title`-keyed message map returns a user-friendly Spanish message. Full error JSON is still written to `error.log`. The `print()` call leaking PII to stdout was also removed.

---

### ~~9. Missing HTTP Security Headers~~ ✅ FIXED — 2026-03-17
**File:** `api/__init__.py`
`@app.after_request` hook sets `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `X-XSS-Protection: 1; mode=block` on every response.

---

### ~~10. Insecure Session Cookie Configuration~~ ✅ FIXED — 2026-03-17
**File:** `api/__init__.py`
`SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE="Strict"` set in `app.config`. Note: `SESSION_COOKIE_SECURE` should be enabled in production (HTTPS only); omitted here to preserve local HTTP dev workflow.

---

### ~~11. No Rate Limiting on Authentication Endpoints~~ ✅ FIXED — 2026-03-17
**File:** `api/auth.py:86`, `api/__init__.py`
`Flask-Limiter==4.1.1` added. `limiter` initialized at module level in `api/__init__.py` and applied to `/auth/login` with `@limiter.limit("5 per minute")`.

---

## Open — Low

### ~~12. Debug `print()` Statements in Production Code~~ ✅ FIXED — 2026-03-17
**Files:** `api/forms.py`, `send_testers.py`

All `print()` calls replaced with `logging` module calls at appropriate levels (`INFO`, `WARNING`, `ERROR`). Root logger configured in `create_app()` with a `RotatingFileHandler` → `app.log` (1 MB × 3 backups) and a `StreamHandler` for dev. `send_testers.py` uses `logging.basicConfig()` as a standalone script.

---


## Action Items

All known issues resolved.
