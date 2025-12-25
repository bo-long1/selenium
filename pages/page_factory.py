"""
Helper functions for lazy page object initialization.
Thread-safe page object management for Behave context.
"""
from pages.heroku import HerokuPage
from pages.orangehrm import OrangeHRMPage

def get_heroku_page(context):
    if not hasattr(context, 'heroku_page'):
        context.heroku_page = HerokuPage(context) 
    return context.heroku_page

def get_orangehrm_page(context):
    """Get or create OrangeHRM page object instance."""
    if not hasattr(context, 'orangehrm_page'):
        context.orangehrm_page = OrangeHRMPage(context)
    return context.orangehrm_page