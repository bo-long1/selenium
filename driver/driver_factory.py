"""
WebDriver factory for creating and configuring browser instances.

Supports:
- Chrome and Edge browsers
- Automatic driver management via webdriver-manager
- Fallback to local drivers when offline
- Proxy configuration
- Custom timeouts and window sizing
- Browser console logging for debugging
"""
import os
import shutil
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from common.utils import load_settings


# ============================================================================
# LOGGER
# ============================================================================
logger = logging.getLogger(__name__)


# ============================================================================
# COMMON BROWSER OPTIONS
# ============================================================================
def _apply_common_options(options, browser_opts: dict):
    """Apply common browser options for Chrome/Edge."""
    # Headless mode
    if browser_opts.get('headless'):
        options.add_argument('--headless=new')
    
    # Incognito/InPrivate mode
    if browser_opts.get('incognito'):
        options.add_argument('--incognito')
    
    # Disable notifications
    if browser_opts.get('disable_notifications'):
        options.add_argument('--disable-notifications')
    
    # Stability options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Enable browser console logging
    options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL',
        'performance': 'ALL'
    })


def _strip_scheme(proxy_url: str) -> str:
    """Return host:port from a proxy URL string that may include scheme."""
    try:
        parsed = urlparse(proxy_url)
        if parsed.hostname and parsed.port:
            return f"{parsed.hostname}:{parsed.port}"
        # If no scheme provided, assume input is already host:port
        return proxy_url
    except Exception:
        return proxy_url


def _apply_proxy(options, proxy_cfg: dict):
    """Apply proxy settings to driver options/capabilities.

    Supports keys: http, https, ftp, socks. Values can be full URLs or host:port.
    """
    if not proxy_cfg:
        return

    p = Proxy()
    p.proxy_type = ProxyType.MANUAL

    http = proxy_cfg.get('http') or proxy_cfg.get('HTTP')
    https = proxy_cfg.get('https') or proxy_cfg.get('HTTPS')
    ftp = proxy_cfg.get('ftp') or proxy_cfg.get('FTP')
    socks = proxy_cfg.get('socks') or proxy_cfg.get('SOCKS')

    if http:
        p.http_proxy = _strip_scheme(http)
    if https:
        p.ssl_proxy = _strip_scheme(https)
    if ftp:
        p.ftp_proxy = _strip_scheme(ftp)
    if socks:
        p.socks_proxy = _strip_scheme(socks)

    # Attach to capabilities
    options.set_capability('proxy', p.to_capabilities()['proxy'])


def _apply_window_size(driver, window_size):
    """Apply window size configuration to driver."""
    if window_size == 'maximize':
        try:
            driver.maximize_window()
        except Exception as e:
            logger.warning(f'Could not maximize window: {e}')
    elif isinstance(window_size, str) and 'x' in window_size:
        try:
            width, height = window_size.split('x')
            driver.set_window_size(int(width), int(height))
        except Exception as e:
            logger.warning(f'Could not set window size {window_size}: {e}')


def _apply_timeouts(driver, timeouts: dict):
    """Apply timeout configurations to driver."""
    if timeouts.get('implicit_wait'):
        driver.implicitly_wait(timeouts['implicit_wait'])
    
    if timeouts.get('page_load_timeout'):
        driver.set_page_load_timeout(timeouts['page_load_timeout'])
    
    if timeouts.get('script_timeout'):
        driver.set_script_timeout(timeouts['script_timeout'])


# ============================================================================
# DRIVER SERVICE MANAGEMENT
# ============================================================================
def _get_chrome_service(version: str = None) -> ChromeService:
    """Get ChromeDriver service with fallback to local driver."""
    try:
        manager = ChromeDriverManager(version=version) if version and version != 'latest' else ChromeDriverManager()
        driver_path = manager.install()
        
        # Fix: webdriver_manager sometimes returns wrong file path
        if driver_path and not driver_path.endswith('chromedriver.exe'):
            driver_dir = os.path.dirname(driver_path)
            correct_path = os.path.join(driver_dir, 'chromedriver.exe')
            if os.path.exists(correct_path):
                driver_path = correct_path
                logger.debug(f'Corrected ChromeDriver path: {driver_path}')
        
        logger.info(f'Using ChromeDriver: {driver_path}')
        return ChromeService(driver_path)
    
    except Exception as e:
        logger.warning(f'webdriver-manager failed to install chromedriver: {e}')
        
        # Fallback to local driver
        local_driver = shutil.which('chromedriver') or shutil.which('chromedriver.exe')
        if local_driver:
            logger.info(f'Using local chromedriver: {local_driver}')
            return ChromeService(local_driver)
        
        raise RuntimeError(
            'Failed to download chromedriver via webdriver-manager.\n'
            'No chromedriver found on PATH. Please ensure:\n'
            '1. You have internet access, OR\n'
            '2. chromedriver is installed locally and added to your PATH\n'
            f'Original error: {e}'
        )


def _get_edge_service(version: str = None) -> EdgeService:
    """Get EdgeDriver service with fallback to local driver."""
    try:
        manager = EdgeChromiumDriverManager(version=version) if version and version != 'latest' else EdgeChromiumDriverManager()
        driver_path = manager.install()
        
        logger.info(f'Using EdgeDriver: {driver_path}')
        return EdgeService(driver_path)
    
    except Exception as e:
        logger.warning(f'webdriver-manager failed to install msedgedriver: {e}')
        
        # Fallback to local driver
        local_driver = shutil.which('msedgedriver') or shutil.which('msedgedriver.exe')
        if local_driver:
            logger.info(f'Using local msedgedriver: {local_driver}')
            return EdgeService(local_driver)
        
        raise RuntimeError(
            'Failed to download msedgedriver via webdriver-manager.\n'
            'No msedgedriver found on PATH. Please ensure:\n'
            '1. You have internet access, OR\n'
            '2. msedgedriver is installed locally and added to your PATH\n'
            '3. Or switch to Chrome in config/test_setting.json\n'
            f'Original error: {e}'
        )


# ============================================================================
# BROWSER-SPECIFIC DRIVERS
# ============================================================================
def create_chrome_driver(browser_opts: dict, timeouts: dict, proxy_settings: dict | None = None) -> webdriver.Chrome:
    """Create and configure Chrome WebDriver."""
    version = browser_opts.get('version')
    service = _get_chrome_service(version)
    
    options = ChromeOptions()
    _apply_common_options(options, browser_opts)
    if browser_opts.get('proxy') and proxy_settings:
        _apply_proxy(options, proxy_settings)
    
    driver = webdriver.Chrome(service=service, options=options)
    
    _apply_timeouts(driver, timeouts)
    _apply_window_size(driver, browser_opts.get('window_size', 'maximize'))
    
    return driver


def create_edge_driver(browser_opts: dict, timeouts: dict, proxy_settings: dict | None = None) -> webdriver.Edge:
    """Create and configure Edge WebDriver."""
    version = browser_opts.get('version')
    service = _get_edge_service(version)
    
    options = EdgeOptions()
    _apply_common_options(options, browser_opts)
    if browser_opts.get('proxy') and proxy_settings:
        _apply_proxy(options, proxy_settings)
    
    driver = webdriver.Edge(service=service, options=options)
    
    _apply_timeouts(driver, timeouts)
    _apply_window_size(driver, browser_opts.get('window_size', 'maximize'))
    
    return driver


# ============================================================================
# MAIN FACTORY FUNCTION
# ============================================================================
def create_driver_from_settings():
    """Create WebDriver based on test_setting.json configuration."""
    settings = load_settings()
    browser_opts = settings.get('browser_options', {})
    timeouts = settings.get('timeouts', {})
    browser_type = browser_opts.get('browser_type', 'chrome').lower()
    proxy_settings = settings.get('proxy_settings', {})
    
    logger.debug(f'Creating {browser_type} WebDriver...')
    
    if browser_type == 'chrome':
        return create_chrome_driver(browser_opts, timeouts, proxy_settings)
    
    elif browser_type == 'edge':
        return create_edge_driver(browser_opts, timeouts, proxy_settings)
    
    else:
        raise ValueError(
            f'Unsupported browser type: {browser_type}\n'
            f'Supported browsers: chrome, edge'
        )
