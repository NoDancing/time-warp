# Bloat Analysis: "Weird Crap" Found

## Summary
This is a REST API-only project (Django + DRF), but it includes several Django components typically used for web applications with HTML templates, sessions, and authentication. Since this is API-only, many of these are unnecessary.

---

## 1. Unused Code in `apps/server/archive/api/views.py`

### Unused Function
- **`utc_now_z()`** (line 20-21): Defined but never called. The code uses `dt_to_z()` instead.

### Unused Import
- **`uuid4`** (line 4): Imported but never used in views.py. It's only used in `models.py` for generating public IDs.

---

## 2. Unnecessary Django Apps (in `config/settings.py`)

These Django contrib apps are included but not used in an API-only project:

- **`django.contrib.auth`**: No authentication is implemented (no login, no user accounts)
- **`django.contrib.sessions`**: No session management needed for stateless API
- **`django.contrib.messages`**: No flash messages needed for API
- **`django.contrib.staticfiles`**: No static files (CSS, JS, images) are served

**Note**: `django.contrib.contenttypes` is likely needed by Django internally, so keep it.

---

## 3. Unnecessary Middleware (in `config/settings.py`)

- **`django.contrib.auth.middleware.AuthenticationMiddleware`**: No authentication system
- **`django.contrib.messages.middleware.MessageMiddleware`**: No messages system
- **`django.middleware.csrf.CsrfViewMiddleware`**: DRF handles CSRF differently for APIs (can use `csrf_exempt` or DRF's own CSRF handling)

---

## 4. Unnecessary Template Configuration (in `config/settings.py`)

- **`TEMPLATES`** (lines 30-37): Entire template configuration is unused. This is a JSON API, not an HTML-serving application.

---

## 5. Empty Admin File

- **`apps/server/archive/admin.py`**: Contains only an unused import:
  ```python
  from django.contrib import admin
  # Register your models here.
  ```
  
  Since no models are registered and the project doesn't use Django admin, this import is unnecessary.

---

## 6. ASGI File (Minor)

- **`apps/server/config/asgi.py`**: Present but likely not needed if only using WSGI. However, this might be intentional for future async support, so it's borderline.

---

## Recommendations

### High Priority (Definitely Remove)
1. Remove unused `utc_now_z()` function from `views.py`
2. Remove unused `uuid4` import from `views.py`
3. Remove unused Django apps: `auth`, `sessions`, `messages`, `staticfiles`
4. Remove unused middleware: `AuthenticationMiddleware`, `MessageMiddleware`, `CsrfViewMiddleware`
5. Remove `TEMPLATES` configuration
6. Clean up `admin.py` (remove unused import)

### Medium Priority (Consider Removing)
- Remove `STATIC_URL` setting if not needed
- Consider removing ASGI if not planning async support

### Impact
Removing these will:
- Reduce Django startup overhead
- Make the codebase cleaner and more aligned with "API-only" purpose
- Reduce confusion about what the project actually does
- Follow Django best practices for API-only projects

---

## What to Keep

- `django.contrib.contenttypes` - Likely needed by Django internally
- `django.middleware.security.SecurityMiddleware` - Good security practice
- `django.middleware.common.CommonMiddleware` - Useful for API too
- `rest_framework` - Core dependency
- `archive` - Your app

---

## Additional Configuration Required

After removing `django.contrib.auth`, DRF needs explicit configuration to work without Django's auth system. Added to `settings.py`:

```python
REST_FRAMEWORK = {
    "UNAUTHENTICATED_USER": None,  # Disable Django auth user model requirement
    "DEFAULT_AUTHENTICATION_CLASSES": [],  # No authentication required
    "DEFAULT_PERMISSION_CLASSES": [],  # No permissions required
}
```

This tells DRF to not require Django's User model for unauthenticated requests.

