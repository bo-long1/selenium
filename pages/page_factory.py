"""
Helper functions for lazy page object initialization.
Thread-safe page object management for Behave context.
"""
from pages.heroku import HerokuPage

def get_heroku_page(context):
    """Get or create HerokuPage instance (lazy initialization)."""
    if not hasattr(context, 'heroku_page'):
        context.heroku_page = HerokuPage(context.driver)
    return context.heroku_page