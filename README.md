# Jasiri Django storefront

The legacy standalone HTML storefront and its assets are kept under `front/`.
Django serves the database-backed storefront from the project root using its
templates and assets under `store/`. The Django app keeps its own copies of the
stylesheet and required images under `store/static/store/`; update those copies
when changing the original assets.

## Run locally

From the project folder, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the storefront and
`http://127.0.0.1:8000/admin/` to manage products. The first migration loads
the 16 tee and jacket products shown on the existing catalog pages. Product
images use paths from the existing `Mwanzocollection` folder.

The admin supports adding, editing, hiding, and removing products. The shop
pages and cart are served by Django; cart contents are stored in the visitor's
session. Checkout is only a placeholder: payment processing and order
placement are not configured.

## Accounts and email

Visitors can create an account at `/accounts/register/`. The account stays
inactive until its email verification link is used. Sign-in, sign-out, password
reset, password change, and the protected account page are available under
`/accounts/`. Product browsing and the cart remain available without signing in.

For local email testing, Django writes emails to the terminal unless SMTP
credentials are configured. To use Gmail SMTP in PowerShell, set the address
and a Gmail app password (not your regular Gmail password) before starting
Django:

```powershell
$env:GMAIL_ADDRESS = "you@example.com"
$env:GMAIL_APP_PASSWORD = "your-app-password"
```

Alternatively, configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD`, and `EMAIL_USE_TLS` for your email provider. Set
`DEFAULT_FROM_EMAIL` to the verified sender address. Do not commit credentials;
use environment variables locally and your hosting provider's secret manager in
production. The newsletter welcome and account verification emails use paired
text and HTML templates under `store/templates/emails/`; password reset email
templates are under `store/templates/registration/`.

## Before deployment

Set `DJANGO_SECRET_KEY` to a private random value, set `DJANGO_DEBUG=false`,
and set `DJANGO_ALLOWED_HOSTS` to the deployed hostnames. Configure HTTPS,
production static-file serving, and a production database before launch.
Secure session and CSRF cookies are enabled when `DJANGO_DEBUG=false`. Configure
the production database and HTTPS before launch, and do not use Django's
development server in production.

On Vercel, Django also allows the exact deployment hostname from Vercel's
`VERCEL_URL` environment variable. Add any custom domain to
`DJANGO_ALLOWED_HOSTS` as a comma-separated hostname list (without `https://`),
then redeploy.

## Tests

```powershell
python manage.py test
```
