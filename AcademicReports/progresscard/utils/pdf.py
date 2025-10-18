# exams/utils/pdf.py
import pdfkit
from django.template import engines, Context
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from urllib.parse import urljoin

# 


# import pdfkit
# from django.template import engines
# from django.conf import settings

# def get_pdfkit_config():
#     wkhtml = getattr(settings, "WKHTMLTOPDF_CMD", None)
#     if wkhtml:
#         return pdfkit.configuration(wkhtml=wkhtml)
#     return None  # pdfkit will use PATH

# def render_template_from_db(html_template_text, css_text,context, request=None):
#     """
#     Render stored HTML (Django template syntax) and optionally prepend CSS.
#     `context` MUST be a plain dict.
#     """
#     if not isinstance(context, dict):
#         # defensive: convert QueryDict/Context-like to plain dict where possible
#         try:
#             context = dict(context)
#         except Exception:
#             # if conversion fails, raise helpful error
#             raise TypeError("context must be a dict")

#     django_engine = engines["django"]
#     tpl_text = f"<style>{css_text or ''}</style>\n" + (html_template_text or "")
#     # tpl_text = html_template_text or ""
#     tpl = django_engine.from_string(tpl_text)

#     # IMPORTANT: pass plain dict, NOT django.template.Context
#     rendered = tpl.render(context)
#     return rendered

# def html_to_pdf_bytes(rendered_html, request=None):
#     """
#     Produce PDF bytes using pdfkit. Use request to set base_url if needed.
#     """
#     config = get_pdfkit_config()
#     options = {
#         "enable-local-file-access": None,
#         "page-size": "A4",
#         "encoding": "UTF-8",
#         "margin-top": "10mm",
#         "margin-bottom": "10mm",
#         "margin-left": "10mm",
#         "margin-right": "10mm",
#     }

#     # pdfkit.from_string returns bytes when second arg is False
#     pdf_bytes = pdfkit.from_string(rendered_html, False, configuration=config, options=options)
#     return pdf_bytes



# def get_pdfkit_config():
#     wkhtml = getattr(settings, "WKHTMLTOPDF_CMD", None)
#     if wkhtml:
#         return pdfkit.configuration(wkhtml=wkhtml)
#     return None  # pdfkit will use PATH


# def render_template_from_db(html_template_text, css_text, context, request=None):
#     """Render stored HTML and CSS using Django template engine."""
#     if not isinstance(context, dict):
#         try:
#             context = dict(context)
#         except Exception:
#             raise TypeError("context must be a plain dict")

#     django_engine = engines["django"]
#     tpl_text = f"<style>{css_text or ''}</style>\n" + (html_template_text or "")
#     tpl = django_engine.from_string(tpl_text)
#     rendered = tpl.render(context)
#     return rendered


# def html_to_pdf_bytes(rendered_html, request=None):
#     """Convert HTML string to PDF bytes using pdfkit."""
#     config = get_pdfkit_config()
#     options = {
#         "enable-local-file-access": None,
#         "page-size": "A4",
#         "encoding": "UTF-8",
#         # "margin-top": "10mm",
#         # "margin-bottom": "10mm",
#         # "margin-left": "10mm",
#         # "margin-right": "10mm",
#     }

#     return pdfkit.from_string(rendered_html, False, configuration=config, options=options)



import pdfkit
from django.conf import settings
from django.template import engines
from django.templatetags.static import static
from django.utils.html import escape


# def get_pdfkit_config():
#     """
#     Load pdfkit configuration if WKHTMLTOPDF_CMD is set in Django settings.
#     Example:
#         WKHTMLTOPDF_CMD = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
#     """
#     wkhtml = getattr(settings, "WKHTMLTOPDF_CMD", None)
#     if wkhtml:
#         return pdfkit.configuration(wkhtml=wkhtml)
#     return None


# def render_template_from_db(html_template_text, css_text, context, request=None):
#     """
#     Render HTML template and CSS (stored in DB) using Django's template engine.
#     Injects absolute static URLs and site base URL for images and assets.
#     """
#     if not isinstance(context, dict):
#         context = dict(context)

#     # Add useful context paths
#     if request:
#         base_url = request.build_absolute_uri("/")
#         context.update({
#             "base_url": base_url,
#             "static_url": request.build_absolute_uri(static("")),
#             "logo_url": request.build_absolute_uri(static("images/schoolLogo.png")),
#         })
#     else:
#         context.update({
#             "base_url": "http://127.0.0.1:8000/",
#             "static_url": "http://127.0.0.1:8000/static/",
#             "logo_url": "http://127.0.0.1:8000/static/images/schoolLogo.png",
#         })

#     # Combine CSS + HTML
#     full_html = f"<style>{css_text or ''}</style>\n" + (html_template_text or "")
    
#     django_engine = engines["django"]
#     template = django_engine.from_string(full_html)
#     rendered_html = template.render(context)

#     return rendered_html


# def html_to_pdf_bytes(rendered_html, request=None):
#     """
#     Convert a rendered HTML string into PDF bytes using pdfkit.
#     Ensures static and media URLs are correctly resolved.
#     """
#     config = get_pdfkit_config()
#     base_url = request.build_absolute_uri("/") if request else "http://127.0.0.1:8000/"

#     # Replace relative paths with absolute URLs
#     rendered_html = rendered_html.replace('src="/static/', f'src="{base_url}static/')
#     rendered_html = rendered_html.replace('href="/static/', f'href="{base_url}static/')

#     options = {
#         "enable-local-file-access": None,   # ✅ Required for static images
#         "page-size": "A4",
#         "encoding": "UTF-8",
#         "print-media-type": None,
#         "quiet": None,                      # ✅ Suppresses extra console logs
#         "margin-top": "8mm",
#         "margin-bottom": "8mm",
#         "margin-left": "8mm",
#         "margin-right": "8mm",
#     }

#     try:
#         pdf_bytes = pdfkit.from_string(rendered_html, False, configuration=config, options=options)
#         return pdf_bytes
#     except Exception as e:
#         raise RuntimeError(f"PDF generation failed: {escape(str(e))}")


# your_app/utils/pdf_utils.py
import os
import pdfkit
from django.conf import settings
from django.template import engines
from django.templatetags.static import static
from django.contrib.staticfiles import finders

def get_pdfkit_config():
    wkhtml = getattr(settings, "WKHTMLTOPDF_CMD", None)
    if wkhtml:
        return pdfkit.configuration(wkhtml=wkhtml)
    return None  # pdfkit will use PATH

def load_local_bootstrap_css():
    """
    Find the local bootstrap file we downloaded and return its text.
    """
    # path relative to static folder used earlier
    rel_path = "bootstrap/css/bootstrap.min.css"
    # try django staticfiles finders first (works in dev and when using collectstatic)
    found = finders.find(rel_path)
    if found and os.path.exists(found):
        with open(found, "r", encoding="utf-8") as f:
            return f.read()
    # fallback: build from STATICFILES_DIRS
    fallback = os.path.join(settings.BASE_DIR, "static", rel_path)
    if os.path.exists(fallback):
        with open(fallback, "r", encoding="utf-8") as f:
            return f.read()
    return ""  # not found

def render_template_from_db(html_template_text, css_text, context, request=None):
    """
    Render stored HTML and CSS using Django template engine.
    This injects local Bootstrap CSS inline (so wkhtmltopdf doesn't need CDNs).
    """
    if not isinstance(context, dict):
        context = dict(context)

    # prepare base absolute urls for static references in HTML
    if request:
        base_url = request.build_absolute_uri("/")
        context["base_url"] = base_url
        context["static_url"] = request.build_absolute_uri(static(""))
        # useful logo absolute URL
        try:
            context["logo_url"] = request.build_absolute_uri(static("images/schoolLogo.png"))
        except Exception:
            context["logo_url"] = request.build_absolute_uri(static(""))
    else:
        base_url = "http://127.0.0.1:8000/"
        context["base_url"] = base_url
        context["static_url"] = base_url + "static/"
        context["logo_url"] = base_url + "static/images/schoolLogo.png"

    # load local bootstrap CSS once
    bootstrap_css = load_local_bootstrap_css()

    # Build full HTML: put bootstrap + user css in a <style> block
    full_html = (
        "<!doctype html>\n<html>\n<head>\n<meta charset='utf-8'>\n"
        f"<style>\n{bootstrap_css}\n{css_text or ''}\n</style>\n"
        "</head>\n<body>\n"
        + (html_template_text or "")
        + "\n</body>\n</html>"
    )

    django_engine = engines["django"]
    tpl = django_engine.from_string(full_html)
    rendered = tpl.render(context)
    # replace relative static urls to absolute so wkhtmltopdf can fetch resources
    rendered = rendered.replace('src="/static/', f'src="{base_url}static/')
    rendered = rendered.replace("src='/static/", f"src='{base_url}static/")
    rendered = rendered.replace('href="/static/', f'href="{base_url}static/')
    rendered = rendered.replace("href='/static/", f"href='{base_url}static/")
    return rendered

def html_to_pdf_bytes(rendered_html, request=None):
    """
    Convert rendered HTML to PDF bytes using pdfkit/wkhtmltopdf
    """
    config = get_pdfkit_config()
    options = {
        "enable-local-file-access": "",   # allow local file reading
        "page-size": "A4",
        "encoding": "UTF-8",
        "print-media-type": "",
        "margin-top": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
        "margin-right": "10mm",
        "quiet": "",
    }

    # if request provided, base_url param isn't supported by your wkhtml version,
    # so ensure rendered_html has absolute URLs injected by render_template_from_db.
    return pdfkit.from_string(rendered_html, False, configuration=config, options=options)
