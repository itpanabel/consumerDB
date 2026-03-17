# Security Audit Report

**Application:** consumerDB (Flask)
**Initial Audit:** 2026-03-15
**Last Reviewed:** 2026-03-17 (rev 3)
**Auditor:** Claude Code (claude-sonnet-4-6)

---

## Summary

| Severity | Open | Fixed |
|----------|------|-------|
| Critical | 0 | 2 |
| High | 7 | 5 |
| Medium | 5 | 1 |
| Low | 2 | 2 |
| **Total** | **14** | **10** |

---

## Fixed

### ~~No CSRF Protection~~ ✅ FIXED — 2026-03-17
**Files:** `api/__init__.py`, all 18 HTML templates
`CSRFProtect(app)` initialized in the app factory. `{{ csrf_token() }}` hidden input added to every form: auth (login, register), beautyadvisors (create, update), brands (create, update), entity (create, update), pos (create, update), stores (create, update), testers (create, update, import), forms (panama, colombia, trequest).

---

### ~~SQL Injection via String Formatting~~ ✅ FIXED — 2026-03-17
**Files:** `api/forms.py:43-46`, `send_testers.py:41`
All queries now use parameterized `?` placeholders. No string interpolation of user input.

---

### ~~Missing `@login_required` on `/entity/create`~~ ✅ FIXED — 2026-03-17
**File:** `api/entity.py:41`
`@login_required` decorator added.

---

### ~~Missing `@login_required` on `/testers/export_resquest`~~ ✅ FIXED — 2026-03-17
**File:** `api/testers.py:211`
`@login_required` decorator added.

---

### ~~Missing `@login_required` on `/entity/delete`~~ ✅ FIXED — 2026-03-17
**File:** `api/entity.py:104`
`@login_required` decorator added.

---

### ~~URL Route Typo `/detele` in all blueprints~~ ✅ FIXED — 2026-03-17
**Files:** `api/testers.py:199`, `api/stores.py:117`, `api/pos.py:118`, `api/brands.py:136`
Route corrected to `/<id>/delete` in all four blueprints.

---

### ~~SQL Injection in `send_testers.py`~~ ✅ FIXED — 2026-03-17
**File:** `send_testers.py:41`
Query now uses parameterized `?` placeholder for `subsidiary`.

---

### ~~No Type Validation on `subsidiaryCode`~~ ✅ FIXED — 2026-03-17
**File:** `api/forms.py:42-44`
`request.args.get("country", type=int)` now used, with an explicit `abort(400)` when the value is missing or non-numeric.

---

### ~~`cursor.description` Accessed After `conn.close()` — Script Crash~~ ✅ FIXED — 2026-03-17
**File:** `send_testers.py:42,53` and `send_testers.py:111`
Column headers are now captured into a `headers` variable before the connection is closed. Also fixed a second bug: Colombia's trigger condition compared a `date` object to an `int` (`current_date == last_day`) which was always `False` — corrected to `current_date.day ==`.

---

## Open — High

### 2. Open User Registration — No Admin Gate
**File:** `api/auth.py:45`

The `/auth/register` endpoint is publicly accessible with no authentication check. Any anonymous visitor can create a user account and gain access to the admin panel.

**Fix:** Protect the register route with `@login_required` and restrict it to admin-only, or remove self-registration entirely.

---

### 3. Hardcoded Role Check via Username String Comparison
**Files:** `api/testers.py:18,91`, `api/brands.py:18`

Role-based access control is implemented by comparing the username to the hardcoded string `"admin"`. Any user named `"admin"` gets full access; all others are restricted regardless of intent. This is not a proper RBAC implementation.

```python
if g.user['username'] != "admin":  # Fragile
```

**Fix:** Add a `role` column to the `USERS` table (`'admin'` / `'user'`) and check `g.user['role'] == 'admin'`.

---

### 4. `index` Routes Access `g.user` Without `@login_required`
**Files:** `api/testers.py:14-18`, `api/brands.py:13-18`

The `index` functions for both testers and brands access `g.user['username']` without `@login_required`. If an unauthenticated user hits these routes, `g.user` is `None`, raising an `AttributeError` and leaking a stack trace in debug mode.

**Fix:** Add `@login_required` to the `index` functions in `testers.py` and `brands.py`.

---

### 5. Unvalidated CSV Delimiter from User Input
**File:** `api/testers.py:117,135`

The CSV delimiter is taken directly from form input and passed to `csv.reader` without any validation or whitelisting.

```python
csv_delimeter = request.form["csvDelimeter"]  # No validation
reader = csv.reader(file, delimiter=csv_delimeter)
```

**Fix:** Whitelist the allowed delimiters:
```python
allowed = [',', ';', '\t', '|']
csv_delimeter = request.form.get("csvDelimeter", ",")
if csv_delimeter not in allowed:
    abort(400)
```

---

### 7. Missing Subsidiary Ownership Check in `testers.update()`
**File:** `api/testers.py:155-195`

The `update()` function loads a tester record by `id` from the URL without verifying it belongs to the requesting user's subsidiary. A user from subsidiary A can manipulate the `id` parameter to update a tester record belonging to subsidiary B.

**Fix:** After loading the tester record, verify ownership:
```python
if g.user['username'] != 'admin' and tester['subsidiaryid'] != userCountry:
    abort(403)
```

---

### 8. `import_testers` Deletes All Subsidiaries' Data
**File:** `api/testers.py:131`

The import endpoint runs `DELETE FROM TESTERS` with no subsidiary scoping before re-importing from the uploaded CSV. Any logged-in user from any subsidiary can wipe the entire tester table for all subsidiaries.

```python
db.execute("DELETE FROM TESTERS")  # Wipes all subsidiaries
```

**Fix:** Scope the delete to the user's own subsidiary:
```python
db.execute("DELETE FROM TESTERS WHERE subsidiaryid = ?", (userCountry,))
```

---

### 9. `ALLOWED_EXTENSIONS` Defined but Never Checked
**File:** `api/testers.py:111`

`ALLOWED_EXTENSIONS = {'csv'}` is declared inside `import_testers()` but never used to validate the uploaded file's extension. Any file type can be uploaded.

```python
ALLOWED_EXTENSIONS = {'csv'}  # Defined but never enforced
```

**Fix:** Validate the file extension before saving:
```python
if not ('.' in csv_filename and csv_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
    flash("Solo se permiten archivos CSV", "alert-danger")
    return redirect("/testers/import_testers")
```

---

## Open — Medium

### 10. Hardcoded Mailchimp List IDs and Group IDs in Source Code
**File:** `api/forms.py:22-27`

Sensitive Mailchimp configuration values are hardcoded in source:
```python
LIST_ID_PA = "4b890a1b03"
LIST_ID_CO = "cae142989c"
LIST_ID_CR = "061656a504"
GROUP_ID_PA = "383283a2bd"
```

Anyone with repository access can use these IDs against the Mailchimp API directly.

**Fix:** Move all to `.env` and load with `os.getenv()`.

---

### 11. Sensitive Information Disclosed in Error Messages
**File:** `api/forms.py:254`

The full Mailchimp API error response (including user email and advisor name) is flashed directly to the browser. Error details also written to `error.log` in the working directory.

```python
flash(error.text, "alert-danger")  # Raw API error shown to user
```

**Fix:** Show a generic message to users; keep details server-side only.

---

### 12. Missing HTTP Security Headers
**File:** `api/__init__.py`

No security-related HTTP response headers are set. Missing:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy`
- `Strict-Transport-Security`

**Fix:**
```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

### 13. Insecure Session Cookie Configuration
**File:** `api/__init__.py`

Session cookies have no security flags, making them vulnerable to interception over HTTP and XSS-based theft.

**Fix:**
```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

---

### 14. No Rate Limiting on Authentication Endpoints
**File:** `api/auth.py` (login, register)

Login and registration have no rate limiting, leaving them open to brute-force and credential-stuffing attacks.

**Fix:** Install `Flask-Limiter` and limit sensitive routes:
```python
@limiter.limit("5 per minute")
def login():
```

---

## Open — Low

### 17. Debug `print()` Statements in Production Code
**Files:** `api/forms.py:69,255,277`, `send_testers.py:93,95,101`

Raw `print()` calls output PII (user emails, advisor names, POS data) and full API error payloads to stdout.

**Fix:** Replace with Python's `logging` module configured per environment.

---

### 18. Outdated Dependencies
**File:** `requirements.txt`

Several packages are significantly behind current stable versions (as of 2026-03):
- `Flask==2.3.2` (Aug 2023)
- `SQLAlchemy==2.0.20` (Oct 2023)
- `Werkzeug==2.3.6` (Aug 2023)
- `urllib3==2.0.4` — known CVEs in older versions

**Fix:** Run `pip list --outdated` and update. Use `pip-audit` for CVE scanning.

---

## Action Items

**Priority 1 — Fix immediately:**
1. Restrict or remove open user self-registration (`/auth/register`)

**Priority 2 — Fix soon:**
4. Add `@login_required` to `testers.index` and `brands.index`
5. Enforce file extension validation in `import_testers`
6. Scope `import_testers` delete to the user's own subsidiary
7. Add subsidiary ownership check in `testers.update()`
9. Add HTTP security headers and secure session cookie flags
10. Move hardcoded Mailchimp IDs to `.env`

**Priority 3 — Ongoing maintenance:**
11. Replace hardcoded `"admin"` username check with a proper `role` column
12. Add rate limiting on login/register
13. Add CSV delimiter whitelist in `import_testers`
14. Replace `print()` with structured logging
15. Update outdated dependencies and run `pip-audit`
