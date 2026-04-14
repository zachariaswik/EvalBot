import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="frontend",
    db_url="sqlite:///reflex.db",
    telemetry_enabled=False,
    show_built_with_reflex=False,
    state_auto_setters=False,
    plugins=[SitemapPlugin()],
)
