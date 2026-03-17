# Security Audit Report

**Application:** consumerDB (Flask)
**Initial Audit:** 2026-03-15
**Last Reviewed:** 2026-03-17 (rev 5)
**Auditor:** Claude Code (claude-sonnet-4-6)

---

## Summary

| Severity | Open | Fixed |
|----------|------|-------|
| Critical | 0 | 2 |
| High | 6 | 6 |
| Medium | 5 | 2 |
| Low | 1 | 3 |
| **Total** | **12** | **13** |

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

### 1. Open User Registration — No Admin Gate
**File:** `api/auth.py:45`

`/auth/register` is publicly accessible. Any anonymous visitor can create a user account and gain access to the admin panel.

**Fix:** Add `@login_required` and restrict to admin-only, or disable self-registration entirely.

---

### 2. Hardcoded Role Check via Username String Comparison
**Files:** `api/testers.py:19,92`, `api/brands.py:18`

Role-based access control compares the username to the hardcoded string `"admin"`. This is not proper RBAC.

```python
if g.user['username'] != "admin":  # Fragile
```

**Fix:** Add a `role` column to the `USERS` table and check `g.user['role'] == 'admin'`.

---

### 3. Unvalidated CSV Delimiter from User Input
**File:** `api/testers.py:118,136`

The CSV delimiter is taken from form input with no validation.

**Fix:** Whitelist allowed values:
```python
allowed = [',', ';', '\t', '|']
if csv_delimeter not in allowed:
    abort(400)
```

---

### 4. Missing Subsidiary Ownership Check in `testers.update()`
**File:** `api/testers.py:156-196`

A user from subsidiary A can manipulate the `id` URL parameter to update a tester belonging to subsidiary B.

**Fix:**
```python
if g.user['username'] != 'admin' and tester['subsidiaryid'] != userCountry:
    abort(403)
```

---

### 5. `import_testers` Deletes All Subsidiaries' Data
**File:** `api/testers.py:132`

`DELETE FROM TESTERS` has no subsidiary scoping — any logged-in user can wipe all subsidiaries' testers.

```python
db.execute("DELETE FROM TESTERS")  # Wipes everything
```

**Fix:**
```python
db.execute("DELETE FROM TESTERS WHERE subsidiaryid = ?", (userCountry,))
```

---

### 6. `ALLOWED_EXTENSIONS` Defined but Never Enforced
**File:** `api/testers.py:112`

`ALLOWED_EXTENSIONS = {'csv'}` is declared but never used to validate the uploaded file. Any file type is accepted.

**Fix:**
```python
if not ('.' in csv_filename and csv_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
    flash("Solo se permiten archivos CSV", "alert-danger")
    return redirect("/testers/import_testers")
```

---

## Open — Medium

### 7. Hardcoded Mailchimp List IDs and Group IDs
**File:** `api/forms.py:22-27`

Mailchimp audience and group IDs are hardcoded in source. Anyone with repo access can use them against the Mailchimp API.

**Fix:** Move to `.env` and load with `os.getenv()`.

---

### 8. Sensitive Information Disclosed in Error Messages
**File:** `api/forms.py:254`

Full Mailchimp API error responses (including user email and advisor name) are flashed to the browser.

```python
flash(error.text, "alert-danger")  # Raw API error shown to user
```

**Fix:** Show a generic message; log details server-side only.

---

### 9. Missing HTTP Security Headers
**File:** `api/__init__.py`

No security headers configured (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Content-Security-Policy`, `Strict-Transport-Security`).

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

### 10. Insecure Session Cookie Configuration
**File:** `api/__init__.py`

Session cookies have no `Secure`, `HttpOnly`, or `SameSite` flags.

**Fix:**
```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

---

### 11. No Rate Limiting on Authentication Endpoints
**File:** `api/auth.py`

Login and registration have no rate limiting — vulnerable to brute-force attacks.

**Fix:** Use `Flask-Limiter`:
```python
@limiter.limit("5 per minute")
def login():
```

---

## Open — Low

### 12. Debug `print()` Statements in Production Code
**Files:** `api/forms.py:71,255,277`, `send_testers.py:93,95,101`

`print()` calls output PII (user emails, advisor names, POS data) and full API error payloads to stdout.

**Fix:** Replace with Python's `logging` module configured per environment.

---


## Action Items

**Priority 1 — Fix next:**
1. Restrict `/auth/register` to admin-only or disable self-registration
2. Add file extension enforcement in `import_testers`
3. Scope `import_testers` DELETE to the user's own subsidiary

**Priority 2 — Fix soon:**
4. Add subsidiary ownership check in `testers.update()`
5. Add CSV delimiter whitelist in `import_testers`
6. Add HTTP security headers
7. Configure secure session cookie flags
8. Move hardcoded Mailchimp IDs to `.env`

**Priority 3 — Ongoing maintenance:**
9. Replace hardcoded `"admin"` username check with a proper `role` column
10. Add rate limiting on login/register
11. Replace `print()` with structured logging
