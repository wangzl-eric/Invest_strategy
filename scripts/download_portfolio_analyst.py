#!/usr/bin/env python3
"""Download Portfolio Analyst CSV from IBKR Client Portal.

Usage:
    python scripts/download_portfolio_analyst.py [--no-headless]

Environment Variables:
    IBKR_USERNAME, IBKR_PASSWORD, IBKR_ACCOUNT_ID (required)
    PA_DOWNLOAD_DIR (optional, default: ./data/pa_reports)
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SELECTORS = {
    "username": ['input[name="username"]', 'input[type="text"][placeholder*="username" i]'],
    "password": ['input[name="password"]', 'input[type="password"]'],
    "login_btn": [
        'button[type="submit"]',
        'button:has-text("Log In")',
        'button:has-text("Sign In")',
        'button:has-text("Login")',
        'input[type="submit"]',
        'button.btn-primary',
        'button.primary',
        '[data-testid*="login"]',
        '[data-testid*="signin"]',
        'form button[type="submit"]',
    ],
    "date_start": ['input[name*="start"]', 'input[id*="start"]', 'input[name*="from"]'],
    "date_end": ['input[name*="end"]', 'input[id*="end"]', 'input[name*="to"]'],
    "download_btn": ['button:has-text("Download")', 'button:has-text("Export")', 'a:has-text("Download")'],
    "popup_dismiss": [
        'button:has-text("Close")', 'button:has-text("Next")', 'button:has-text("Got it")',
        'button:has-text("OK")', 'button[aria-label*="close" i]', '.modal-close',
    ],
    "two_fa": [
        'text=Face ID', 'text=Two-Factor', 'text=2FA', 'text=Verify',
        'text=Approve', 'text=Authenticate', '.two-factor', '.face-id',
    ],
}

PA_URLS = [
    "https://www.interactivebrokers.com/portal/portfolio-analyst",
    "https://www.interactivebrokers.com/portal/app/portfolio-analyst",
]

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: Optional[str] = None) -> logging.Logger:
    """Configure logging to console and dated file."""
    log_path = Path(log_dir or os.getenv("PA_LOG_DIR", "./logs"))
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_file = log_path / f"pa_download_{datetime.now():%Y%m%d}.log"
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # Console: INFO level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s │ %(levelname)s │ %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(ch)
    
    # File: DEBUG level
    fh = logging.FileHandler(log_file, mode='a')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(fh)
    
    return logger

logger = setup_logging()

# ============================================================================
# BROWSER HELPERS
# ============================================================================

def try_selectors(page, selectors: list, action: str = "click", value: Optional[str] = None, timeout: int = 3000) -> bool:
    """Try multiple selectors until one works. Returns True on success."""
    for sel in selectors:
        try:
            loc = page.locator(sel)
            # For exact text matching, check if element exists and has exact text
            if "text=" in sel or ":has-text(" in sel:
                # Get all matching elements and filter for exact text match
                all_elements = loc.all()
                for element in all_elements:
                    try:
                        element_text = element.inner_text().strip()
                        # Check if it's an exact match (not containing "performances" or "&")
                        if element.is_visible(timeout=500):
                            # For "报告" or "Report", check exact match
                            if element_text == "报告" or element_text == "Report":
                                if action == "click":
                                    element.click()
                                elif action == "fill" and value:
                                    element.fill(value)
                                logger.debug(f"✓ {action} via {sel} (exact match: '{element_text}')")
                                return True
                            # Also check if it contains "报告" or "Report" but NOT "performances"
                            elif ("报告" in element_text or "Report" in element_text) and "performances" not in element_text.lower() and "&" not in element_text:
                                if action == "click":
                                    element.click()
                                elif action == "fill" and value:
                                    element.fill(value)
                                logger.debug(f"✓ {action} via {sel} (filtered match: '{element_text}')")
                                return True
                    except:
                        continue
            else:
                # Standard selector matching
                if loc.is_visible(timeout=timeout):
                    if action == "click":
                        loc.click()
                    elif action == "fill" and value:
                        loc.fill(value)
                    elif action == "select" and value:
                        page.select_option(sel, value)
                    logger.debug(f"✓ {action} via {sel}")
                    return True
        except Exception:
            continue
    return False


def fast_find_and_click(
    page, 
    selectors: list, 
    description: str, 
    max_attempts: int = 20, 
    refresh_interval_ms: int = 500,
    click_delay_ms: int = 1000
) -> bool:
    """
    Fast refresh cycle to find and click an element.
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        description: Description for logging
        max_attempts: Maximum number of refresh cycles
        refresh_interval_ms: Milliseconds between refresh checks
        click_delay_ms: Milliseconds to wait after clicking
    
    Returns:
        True if element found and clicked, False otherwise
    """
    logger.info(f"Fast cycle: Looking for '{description}'...")
    
    for attempt in range(1, max_attempts + 1):
        # Try each selector
        for selector in selectors:
            try:
                locator = page.locator(selector)
                if locator.is_visible(timeout=500):
                    logger.info(f"✓ Found '{description}' (attempt {attempt}) using: {selector}")
                    locator.click()
                    page.wait_for_timeout(click_delay_ms)
                    return True
            except Exception:
                continue
        
        # If not found, refresh page and try again
        if attempt < max_attempts:
            try:
                page.reload(wait_until="domcontentloaded", timeout=5000)
                page.wait_for_timeout(refresh_interval_ms)
                logger.debug(f"Refresh cycle {attempt}/{max_attempts} - checking for '{description}'...")
            except Exception as e:
                logger.debug(f"Refresh failed: {e}, continuing...")
                page.wait_for_timeout(refresh_interval_ms)
    
    logger.warning(f"✗ Could not find '{description}' after {max_attempts} attempts")
    return False


def dismiss_popups(page, wait_ms: int = 2000):
    """Dismiss any modal/popup dialogs."""
    page.wait_for_timeout(wait_ms)
    if try_selectors(page, SELECTORS["popup_dismiss"], timeout=1000):
        logger.info("Dismissed popup")
        page.wait_for_timeout(1000)


def take_error_screenshot(page, download_path: Path, timestamp: str) -> Optional[Path]:
    """Save screenshot for debugging."""
    try:
        path = download_path / f"error_screenshot_{timestamp}.png"
        page.screenshot(path=str(path), full_page=True)
        logger.info(f"Error screenshot: {path}")
        return path
    except Exception as e:
        logger.warning(f"Could not save screenshot: {e}")
        return None


def wait_for_login(page, max_wait: int = 90) -> bool:
    """
    Wait for login to complete, handling Face ID/2FA.
    Starts fast refresh cycle after 30 seconds if still waiting.
    
    Returns True if login successful, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("⚠️  FACE ID AUTHENTICATION MAY BE REQUIRED")
    logger.info("=" * 60)
    logger.info("If a Face ID prompt appears on your device, please authenticate now")
    logger.info(f"The script will wait up to {max_wait} seconds for completion")
    logger.info("=" * 60)
    
    dashboard_selectors = [
        'text=Portfolio Analyst',
        '[href*="portfolio"]',
        '.account-menu',
        '[data-testid*="dashboard"]',
        'text=Account',
        'text=Positions',
    ]
    two_fa_detected = False
    fast_cycle_started = False
    
    for i in range(max_wait // 5):
        page.wait_for_timeout(5000)
        elapsed = (i + 1) * 5
        
        # Check if logged in
        logged_in = False
        for selector in dashboard_selectors:
            try:
                if page.locator(selector).is_visible(timeout=1000):
                    if elapsed > 10:
                        logger.info(f"✓ Login successful - Face ID completed ({elapsed}s)")
                    else:
                        logger.info(f"✓ Login successful ({elapsed}s)")
                    return True
            except:
                continue
        
        # Check for 2FA indicators on page after 5 seconds
        if elapsed == 5 and not two_fa_detected:
            try:
                page_text = page.inner_text("body").lower()
                if any(term in page_text for term in ["face id", "two-factor", "2fa", "verify", "authenticate", "approve"]):
                    logger.info("⚠️  2FA/Face ID prompt detected on page")
                    logger.info("Please complete Face ID authentication on your device")
                    two_fa_detected = True
            except:
                pass
        
        # Start fast refresh cycle after 30 seconds
        if elapsed >= 30 and not fast_cycle_started:
            logger.info(f"⏳ Still waiting for Face ID authentication... ({elapsed}s)")
            logger.info("   Starting fast refresh cycle to detect login...")
            fast_cycle_started = True
        
        # Fast refresh cycle (every 500ms) after 30 seconds
        if fast_cycle_started:
            # Check login status with fast refresh
            for selector in dashboard_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=500):
                        logger.info(f"✓ Login successful - detected via fast cycle ({elapsed}s)")
                        return True
                except:
                    continue
            
            # Refresh page every 2 seconds during fast cycle
            if elapsed % 2 == 0:
                try:
                    page.reload(wait_until="domcontentloaded", timeout=5000)
                    logger.debug(f"Fast cycle refresh at {elapsed}s - checking for login...")
                except Exception as e:
                    logger.debug(f"Refresh failed: {e}, continuing...")
        else:
            # Progress update every 15s before fast cycle starts
            if elapsed % 15 == 0:
                current_url = page.url.lower()
                if "login" in current_url or "signin" in current_url:
                    logger.info(f"⏳ Still waiting for Face ID authentication... ({elapsed}s)")
                    logger.info("   Check your device for Face ID prompts")
                else:
                    logger.debug(f"Checking login status... ({elapsed}s)")
    
    # Final check
    for selector in dashboard_selectors:
        try:
            if page.locator(selector).is_visible(timeout=2000):
                logger.info(f"✓ Login successful (completed in {max_wait}s)")
                return True
        except:
            continue
    
    logger.error("=" * 60)
    logger.error("✗ LOGIN TIMEOUT")
    logger.error("=" * 60)
    logger.error("Face ID authentication may not have completed")
    logger.error("Please check:")
    logger.error("  1. Face ID prompt appeared on your device")
    logger.error("  2. Face ID was successfully authenticated")
    logger.error("  3. Your IBKR account has Face ID enabled")
    logger.error("=" * 60)
    
    return False


# ============================================================================
# MAIN DOWNLOAD FUNCTION
# ============================================================================

def download_pa_report(
    username: Optional[str] = None,
    password: Optional[str] = None,
    account_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    download_dir: Optional[str] = None,
    headless: bool = True,
) -> Path:
    """
    Download Portfolio Analyst Custom Report CSV from IBKR.
    
    Returns: Path to downloaded CSV file
    Raises: ImportError, ValueError, RuntimeError on failure
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")
    
    # Resolve credentials
    username = username or os.getenv("IBKR_USERNAME")
    password = password or os.getenv("IBKR_PASSWORD")
    account_id = account_id or os.getenv("IBKR_ACCOUNT_ID")
    
    if not all([username, password, account_id]):
        raise ValueError("Missing credentials. Set IBKR_USERNAME, IBKR_PASSWORD, IBKR_ACCOUNT_ID")
    
    # Default dates
    end_date = end_date or datetime.now().strftime("%Y-%m-%d")
    start_date = start_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    # Setup paths
    download_path = Path(download_dir or os.getenv("PA_DOWNLOAD_DIR", "./data/pa_reports"))
    download_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = download_path / f"pa_report_{account_id}_{timestamp}.csv"
    
    logger.info("=" * 60)
    logger.info(f"PA Report: {account_id} | {start_date} → {end_date}")
    logger.info("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True, viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # STEP 1: Login
            logger.info("Step 1/8: Logging in...")
            page.goto("https://www.interactivebrokers.com/portal/", wait_until="networkidle")
            logger.debug(f"Page loaded: {page.url}")
            
            # Check if already logged in
            already_logged_in = False
            try:
                dashboard_indicators = [
                    'text=Portfolio Analyst',
                    '[href*="portfolio"]',
                    '.account-menu',
                    '[data-testid*="dashboard"]',
                ]
                for indicator in dashboard_indicators:
                    try:
                        if page.locator(indicator).is_visible(timeout=2000):
                            logger.info("✓ Already logged in - skipping login step")
                            already_logged_in = True
                            break
                    except:
                        continue
            except:
                pass
            
            if not already_logged_in:
                # Fill username
                username_filled = try_selectors(page, SELECTORS["username"], "fill", username, timeout=5000)
                if username_filled:
                    logger.info("✓ Username filled")
                else:
                    logger.warning("⚠ Could not fill username - check selectors or page structure")
                    logger.debug("Taking screenshot for debugging...")
                    page.screenshot(path=str(download_path / f"debug_username_{timestamp}.png"))
                
                # Fill password
                password_filled = try_selectors(page, SELECTORS["password"], "fill", password, timeout=5000)
                if password_filled:
                    logger.info("✓ Password filled")
                else:
                    logger.warning("⚠ Could not fill password - check selectors or page structure")
                
                if not username_filled or not password_filled:
                    logger.error("Failed to fill credentials - cannot proceed with login")
                    raise RuntimeError("Could not fill username/password fields")
            
                # Click login button - CRITICAL STEP
                logger.info("Clicking Login button...")
                login_clicked = try_selectors(page, SELECTORS["login_btn"], "click", timeout=5000)
                
                if not login_clicked:
                    logger.warning("⚠ Could not click Login button with standard selectors")
                    logger.info("Trying alternative methods...")
                    
                    # Method 1: Try pressing Enter on password field
                    try:
                        page.locator(SELECTORS["password"][0]).press("Enter")
                        logger.info("✓ Pressed Enter key on password field")
                        login_clicked = True
                    except Exception as e:
                        logger.debug(f"Enter key method failed: {e}")
                    
                    # Method 2: Try finding button by text content
                    if not login_clicked:
                        try:
                            buttons = page.locator("button").all()
                            for btn in buttons:
                                try:
                                    text = btn.inner_text().lower()
                                    if any(word in text for word in ["log", "sign", "submit"]):
                                        btn.click()
                                        logger.info(f"✓ Clicked login button via text search: '{text}'")
                                        login_clicked = True
                                        break
                                except:
                                    continue
                        except Exception as e:
                            logger.debug(f"Text-based button search failed: {e}")
                    
                    # Method 3: Try form submission
                    if not login_clicked:
                        try:
                            page.locator("form").first.press("Enter")
                            logger.info("✓ Pressed Enter on form")
                            login_clicked = True
                        except Exception as e:
                            logger.debug(f"Form submission failed: {e}")
                    
                    if not login_clicked:
                        logger.error("=" * 60)
                        logger.error("✗ CRITICAL: Could not click Login button")
                        logger.error("=" * 60)
                        logger.error("All automatic methods failed:")
                        logger.error("  - Standard button selectors")
                        logger.error("  - Enter key on password field")
                        logger.error("  - Text-based button search")
                        logger.error("  - Form submission")
                        logger.error("")
                        logger.error("MANUAL INTERVENTION REQUIRED:")
                        logger.error("  1. The browser window should be visible")
                        logger.error("  2. Please manually click the Login button")
                        logger.error("  3. Complete Face ID if prompted")
                        logger.error("  4. The script will wait 60 seconds for you to complete login")
                        logger.error("=" * 60)
                        
                        # Take screenshot for debugging
                        debug_screenshot = download_path / f"debug_login_button_{timestamp}.png"
                        page.screenshot(path=str(debug_screenshot), full_page=True)
                        logger.info(f"Debug screenshot saved: {debug_screenshot}")
                        
                        # Wait for manual login
                        logger.info("Waiting 60 seconds for manual login...")
                        logger.info("Please click Login and complete Face ID now...")
                        page.wait_for_timeout(60000)
                        logger.info("Continuing after manual wait...")
                
                if login_clicked:
                    logger.info("✓ Login button clicked - Face ID should trigger now")
                    page.wait_for_timeout(2000)  # Brief wait for page to process
                
                # Wait for login (handles Face ID/2FA)
                logger.info("Waiting for login to complete...")
                login_success = wait_for_login(page, max_wait=90)
            else:
                logger.info("Already logged in - proceeding to next step")
                login_success = True
            
            if not login_success:
                current_url = page.url.lower()
                page_title = page.title().lower()
                
                # Check if we're actually logged in (might have succeeded but selector didn't match)
                if "login" not in current_url and "signin" not in current_url:
                    logger.info("✓ Appears to be logged in (not on login page)")
                    logger.info(f"Current URL: {page.url}")
                    login_success = True
                elif "portfolio" in current_url or "dashboard" in current_url or "account" in current_url:
                    logger.info("✓ Appears to be logged in (on dashboard/portfolio page)")
                    login_success = True
                else:
                    logger.error("=" * 60)
                    logger.error("✗ LOGIN FAILED")
                    logger.error("=" * 60)
                    logger.error("Current URL: " + page.url)
                    logger.error("Page title: " + page.title())
                    logger.error("")
                    logger.error("Possible causes:")
                    logger.error("  1. Login button was not clicked")
                    logger.error("  2. Face ID was not completed (check your device)")
                    logger.error("  3. Face ID authentication was denied")
                    logger.error("  4. Invalid username/password")
                    logger.error("  5. 2FA timeout (90 seconds exceeded)")
                    logger.error("")
                    logger.error("Try running with --no-headless to debug")
                    logger.error("=" * 60)
                    raise RuntimeError("Login failed - check credentials or complete Face ID")
            
            # Verify we're logged in before proceeding
            logger.info("Verifying login status before proceeding...")
            current_url = page.url.lower()
            page_title = page.title().lower()
            
            # Multiple checks to confirm we're logged in
            logged_in_indicators = [
                # URL-based checks
                "login" not in current_url and "signin" not in current_url,
                "portfolio" in current_url or "dashboard" in current_url or "account" in current_url,
                # Page element checks
            ]
            
            logged_in = False
            try:
                # Check for dashboard indicators on page
                dashboard_indicators = [
                    'text=Portfolio Analyst',
                    '[href*="portfolio"]',
                    '.account-menu',
                    '[data-testid*="dashboard"]',
                    'text=Account',
                    'text=Positions',
                    'text=Trades',
                ]
                for indicator in dashboard_indicators:
                    try:
                        if page.locator(indicator).is_visible(timeout=2000):
                            logger.info(f"✓ Confirmed logged in (found element: {indicator})")
                            logged_in = True
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Element check error: {e}")
            
            # If element check failed, use URL-based check
            if not logged_in:
                if "login" not in current_url and "signin" not in current_url:
                    logger.info(f"✓ Confirmed logged in (URL check: {page.url})")
                    logged_in = True
                elif "portfolio" in current_url or "dashboard" in current_url:
                    logger.info(f"✓ Confirmed logged in (on dashboard page: {page.url})")
                    logged_in = True
            
            if not logged_in:
                logger.warning("⚠ Could not definitively confirm login status")
                logger.warning(f"Current URL: {page.url}")
                logger.warning(f"Page title: {page.title()}")
                logger.warning("Continuing anyway - script will attempt to proceed")
            else:
                logger.info("✓ Login verified - proceeding to Portfolio Analyst...")
            
            dismiss_popups(page)
            
            # STEP 2: Navigate to Portfolio Analyst (Fast Refresh Cycle)
            logger.info("Step 2/8: Opening Portfolio Analyst (fast refresh cycle)...")
            logger.debug(f"Current URL before navigation: {page.url}")
            
            # Fast cycle: Look for PortfolioAnalyst button
            pa_selectors = [
                'button:has-text("PortfolioAnalyst")',
                'button:has-text("Portfolio Analyst")',
                'a:has-text("PortfolioAnalyst")',
                'a:has-text("Portfolio Analyst")',
                '[href*="portfolio-analyst"]',
                '[href*="portfolio"]',
                'text=PortfolioAnalyst',
                'text=Portfolio Analyst',
                '[data-testid*="portfolio"]',
                '[aria-label*="Portfolio Analyst" i]',
            ]
            
            pa_clicked = fast_find_and_click(
                page, 
                pa_selectors, 
                description="PortfolioAnalyst button",
                max_attempts=20,
                refresh_interval_ms=500,
                click_delay_ms=2000
            )
            
            if not pa_clicked:
                # Fallback: Try direct URL navigation
                logger.warning("Fast cycle failed, trying direct URL navigation...")
                for idx, url in enumerate(PA_URLS, 1):
                    try:
                        logger.debug(f"Trying PA URL {idx}/{len(PA_URLS)}: {url}")
                        page.goto(url, wait_until="networkidle", timeout=15000)
                        if "portfolio" in page.url.lower() or "analyst" in page.url.lower():
                            logger.info(f"✓ Navigated to Portfolio Analyst: {page.url}")
                            pa_clicked = True
                            break
                    except PlaywrightTimeout as e:
                        logger.debug(f"Timeout navigating to {url}: {e}")
                        continue
            
            dismiss_popups(page)
            
            # STEP 3: Click "Reports" or "报告" tab/button
            logger.info("Step 3/8: Looking for 'Reports' or '报告' tab/button...")
            page.wait_for_timeout(3000)  # Wait for page to fully load
            
            # Look for Reports button/tab (English and Chinese)
            # Use exact text matching - avoid "performances & reports" or similar
            # Only match buttons/tabs with exactly "报告" or "Reports" (plural, not singular "Report")
            report_selectors = [
                # Exact text match - must be exactly "报告" or "Reports" (plural), not "performances & reports"
                'button:has-text("^报告$")',  # Button with exactly "报告" (regex anchor)
                'button:has-text("^Reports$")',  # Button with exactly "Reports" (plural, regex anchor)
                'a:has-text("^报告$")',  # Link with exactly "报告"
                'a:has-text("^Reports$")',  # Link with exactly "Reports" (plural)
                # Try exact text matching with locator filter
                'button >> text="报告"',  # Exact match: button with exactly "报告"
                'button >> text="Reports"',  # Exact match: button with exactly "Reports" (plural)
                'a >> text="报告"',  # Exact match: link with exactly "报告"
                'a >> text="Reports"',  # Exact match: link with exactly "Reports" (plural)
                # Aria-label exact matches
                '[aria-label="报告"]',  # Exact aria-label match
                '[aria-label="Reports" i]',  # Exact aria-label match (case-insensitive, plural)
                # Try to find buttons that are NOT "performances & reports"
                'button:not(:has-text("performances")):not(:has-text("&")):has-text("报告")',
                'button:not(:has-text("performances")):not(:has-text("&")):has-text("Reports")',  # Plural
                'a:not(:has-text("performances")):not(:has-text("&")):has-text("报告")',
                'a:not(:has-text("performances")):not(:has-text("&")):has-text("Reports")',  # Plural
                # Fallbacks (but still avoid "performances & reports")
                'button:has-text("报告"):not(:has-text("performances"))',
                'button:has-text("Reports"):not(:has-text("performances"))',  # Plural
                'a:has-text("报告"):not(:has-text("performances"))',
                'a:has-text("Reports"):not(:has-text("performances"))',  # Plural
            ]
            
            report_clicked = try_selectors(page, report_selectors, "click", timeout=5000)
            
            if report_clicked:
                logger.info("✓ Clicked 'Reports' / '报告' tab/button")
                page.wait_for_timeout(2000)  # Wait for Reports section to load
            else:
                logger.warning("Could not find 'Reports' / '报告' button/tab")
                logger.info("Trying to continue - may already be on Reports page...")
            
            dismiss_popups(page)
            
            # STEP 4: Find Custom Reports Panel
            logger.info("Step 4/8: Finding Custom Reports panel...")
            page.wait_for_timeout(2000)  # Wait for Report section to load
            
            # Look for Custom Reports panel
            custom_reports_panel_found = False
            custom_reports_selectors = [
                'text=Custom Reports',
                'text=自定义报告',  # Chinese for Custom Reports
                '[aria-label*="Custom Reports" i]',
                '[aria-label*="自定义报告" i]',
                '.custom-reports',
                '[data-testid*="custom-reports"]',
                '[class*="custom-reports"]',
                '[class*="CustomReports"]',
            ]
            
            for selector in custom_reports_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=3000):
                        logger.info(f"✓ Found Custom Reports panel: {selector}")
                        custom_reports_panel_found = True
                        break
                except:
                    continue
            
            if not custom_reports_panel_found:
                logger.warning("Could not find Custom Reports panel, but continuing...")
                logger.info("Taking screenshot for debugging...")
                try:
                    page.screenshot(path=str(download_path / f"debug_custom_reports_{timestamp}.png"), full_page=True)
                except:
                    pass
            
            dismiss_popups(page)
            
            # STEP 5: Find and Run "custom_report_algo" Custom Report
            logger.info("Step 5/8: Looking for 'custom_report_algo' report...")
            
            # Search for the specific report name
            report_name_selectors = [
                'text="custom_report_algo"',  # Exact match
                'text=custom_report_algo',  # Contains match
                '[aria-label*="custom_report_algo" i]',
                # Look within Custom Reports section
                'text=Custom Reports >> .. >> text=custom_report_algo',
                'text=自定义报告 >> .. >> text=custom_report_algo',
            ]
            
            report_found = False
            report_element = None
            
            # Find the report by name
            for selector in report_name_selectors:
                try:
                    report_element = page.locator(selector).first
                    if report_element.is_visible(timeout=2000):
                        logger.info(f"✓ Found 'custom_report_algo' report: {selector}")
                        report_found = True
                        break
                except:
                    continue
            
            if report_found and report_element:
                # Find Run button associated with this report
                # Try multiple approaches to find Run button in same row/container
                logger.info("Looking for Run button associated with 'custom_report_algo'...")
                
                run_clicked = False
                
                # Strategy 1: Look for Font Awesome Run icon (fa-circle-arrow-right) with data-original-title="Run"
                # The Run button is: <i class="fa fa-circle-arrow-right" data-original-title="Run"></i>
                try:
                    parent = report_element.locator('..')
                    # Look for the icon element directly
                    icon_run_selectors = [
                        # Font Awesome icon with Run tooltip
                        parent.locator('i.fa-circle-arrow-right[data-original-title="Run"]'),
                        parent.locator('i[class*="fa-circle-arrow-right"][data-original-title="Run"]'),
                        parent.locator('i[data-original-title="Run"]'),
                        parent.locator('i.fa-circle-arrow-right'),
                        # Parent button/element containing the icon
                        parent.locator('button:has(i.fa-circle-arrow-right[data-original-title="Run"])'),
                        parent.locator('button:has(i[data-original-title="Run"])'),
                        parent.locator('a:has(i.fa-circle-arrow-right[data-original-title="Run"])'),
                        parent.locator('div:has(i.fa-circle-arrow-right[data-original-title="Run"])'),
                        # Look for clickable element containing the icon
                        parent.locator('[role="button"]:has(i.fa-circle-arrow-right[data-original-title="Run"])'),
                        # Fallback: any element with data-original-title="Run"
                        parent.locator('[data-original-title="Run"]'),
                        parent.locator('[data-original-title*="Run" i]'),
                    ]
                    for icon_sel in icon_run_selectors:
                        try:
                            if icon_sel.is_visible(timeout=1000):
                                logger.info("✓ Found Run icon (Font Awesome fa-circle-arrow-right)")
                                icon_sel.click()
                                page.wait_for_timeout(2000)
                                run_clicked = True
                                break
                        except:
                            continue
                except:
                    pass
                
                # Strategy 2: Parent container approach with Font Awesome icon
                if not run_clicked:
                    try:
                        parent_container = report_element.locator('../..')
                        icon_selectors = [
                            # Font Awesome icon in parent container
                            parent_container.locator('i.fa-circle-arrow-right[data-original-title="Run"]'),
                            parent_container.locator('i[data-original-title="Run"]'),
                            parent_container.locator('button:has(i.fa-circle-arrow-right[data-original-title="Run"])'),
                            parent_container.locator('[data-original-title="Run"]'),
                            # Fallback to aria-label/title
                            parent_container.locator('button[aria-label*="Run" i]'),
                            parent_container.locator('button[title*="Run" i]'),
                        ]
                        for icon_sel in icon_selectors:
                            try:
                                if icon_sel.is_visible(timeout=1000):
                                    logger.info("✓ Found Run icon (parent container approach)")
                                    icon_sel.click()
                                    page.wait_for_timeout(2000)
                                    run_clicked = True
                                    break
                            except:
                                continue
                    except:
                        pass
                
                # Strategy 3: XPath approach - find Font Awesome icon in same row/ancestor
                if not run_clicked:
                    try:
                        # Try XPath to find Font Awesome icon with data-original-title="Run" in ancestor tr or div
                        run_icon = report_element.locator('xpath=ancestor::tr//i[contains(@class, "fa-circle-arrow-right") and @data-original-title="Run"]').first
                        if run_icon.is_visible(timeout=1000):
                            logger.info("✓ Found Run icon (XPath ancestor::tr - Font Awesome)")
                            run_icon.click()
                            page.wait_for_timeout(2000)
                            run_clicked = True
                        else:
                            # Try finding parent button/element
                            run_button = report_element.locator('xpath=ancestor::tr//*[.//i[contains(@class, "fa-circle-arrow-right") and @data-original-title="Run"]]').first
                            if run_button.is_visible(timeout=1000):
                                logger.info("✓ Found Run icon container (XPath ancestor::tr)")
                                run_button.click()
                                page.wait_for_timeout(2000)
                                run_clicked = True
                    except:
                        pass
                
                # Strategy 4: XPath div ancestor approach with Font Awesome icon
                if not run_clicked:
                    try:
                        # Find Font Awesome icon in ancestor div
                        run_icon = report_element.locator('xpath=ancestor::div[contains(@class, "report") or contains(@class, "row")]//i[contains(@class, "fa-circle-arrow-right") and @data-original-title="Run"]').first
                        if run_icon.is_visible(timeout=1000):
                            logger.info("✓ Found Run icon (XPath ancestor::div - Font Awesome)")
                            run_icon.click()
                            page.wait_for_timeout(2000)
                            run_clicked = True
                        else:
                            # Try finding parent element
                            run_button = report_element.locator('xpath=ancestor::div//*[.//i[contains(@class, "fa-circle-arrow-right") and @data-original-title="Run"]]').first
                            if run_button.is_visible(timeout=1000):
                                logger.info("✓ Found Run icon container (XPath ancestor::div)")
                                run_button.click()
                                page.wait_for_timeout(2000)
                                run_clicked = True
                    except:
                        pass
                
                # Strategy 5: Find all Font Awesome Run icons near the report and check proximity
                if not run_clicked:
                    try:
                        # Look for all Font Awesome icons with data-original-title="Run" near the report
                        all_run_icons = page.locator('i.fa-circle-arrow-right[data-original-title="Run"], i[data-original-title="Run"], [data-original-title="Run"]').all()
                        report_box = report_element.bounding_box()
                        
                        for icon_element in all_run_icons:
                            try:
                                if icon_element.is_visible(timeout=500) and report_box:
                                    icon_box = icon_element.bounding_box()
                                    if icon_box:
                                        # Check if they're in similar vertical position (same row) and close horizontally
                                        vertical_diff = abs(report_box['y'] - icon_box['y'])
                                        horizontal_diff = abs(report_box['x'] - icon_box['x'])
                                        
                                        # Same row (vertical diff < 50px) and not too far horizontally (within 500px)
                                        if vertical_diff < 50 and horizontal_diff < 500:
                                            logger.info(f"✓ Found Run icon (proximity check: v_diff={vertical_diff:.0f}px, h_diff={horizontal_diff:.0f}px)")
                                            icon_element.click()
                                            page.wait_for_timeout(2000)
                                            run_clicked = True
                                            break
                            except:
                                continue
                    except:
                        pass
                
                # Strategy 6: Find parent clickable element of Font Awesome icon
                if not run_clicked:
                    try:
                        # Look for the icon and click its parent (button/a/div) if icon itself is not clickable
                        run_icon = page.locator('i.fa-circle-arrow-right[data-original-title="Run"]').first
                        if run_icon.is_visible(timeout=1000):
                            # Try clicking the icon directly first
                            try:
                                logger.info("✓ Found Run icon (direct click)")
                                run_icon.click()
                                page.wait_for_timeout(2000)
                                run_clicked = True
                            except:
                                # If direct click fails, try clicking parent
                                try:
                                    parent_clickable = run_icon.locator('xpath=ancestor::button | ancestor::a | ancestor::div[@role="button"]').first
                                    if parent_clickable.is_visible(timeout=1000):
                                        logger.info("✓ Found Run icon parent (clicking parent element)")
                                        parent_clickable.click()
                                        page.wait_for_timeout(2000)
                                        run_clicked = True
                                except:
                                    pass
                    except:
                        pass
                
                if not run_clicked:
                    logger.warning("Could not find Run button for 'custom_report_algo'")
                    logger.info("Taking screenshot for debugging...")
                    try:
                        page.screenshot(path=str(download_path / f"debug_run_button_{timestamp}.png"), full_page=True)
                    except:
                        pass
                else:
                    # After clicking Run icon, wait for pop-up window and click "Run" button in it
                    logger.info("Waiting for pop-up window after clicking Run icon...")
                    page.wait_for_timeout(2000)  # Wait for pop-up to appear
                    
                    # Look for "Run" button in the pop-up/modal window
                    popup_run_selectors = [
                        'button:has-text("Run")',
                        'button:has-text("运行")',  # Chinese for Run
                        'button[aria-label*="Run" i]',
                        'button[title*="Run" i]',
                        '.modal button:has-text("Run")',
                        '.modal-dialog button:has-text("Run")',
                        '[role="dialog"] button:has-text("Run")',
                        '.popup button:has-text("Run")',
                        'button.primary:has-text("Run")',
                        'button.btn-primary:has-text("Run")',
                        'button[type="submit"]:has-text("Run")',
                        'button[type="button"]:has-text("Run")',
                    ]
                    
                    popup_run_clicked = try_selectors(page, popup_run_selectors, "click", timeout=5000)
                    
                    if popup_run_clicked:
                        logger.info("✓ Clicked 'Run' button in pop-up window")
                        page.wait_for_timeout(3000)  # Wait for report to start generating
                    else:
                        logger.warning("Could not find 'Run' button in pop-up window")
                        logger.info("Pop-up may not have appeared, or button has different text")
                        logger.info("Taking screenshot for debugging...")
                        try:
                            page.screenshot(path=str(download_path / f"debug_popup_run_{timestamp}.png"), full_page=True)
                        except:
                            pass
            else:
                logger.error("Could not find 'custom_report_algo' report in Custom Reports panel")
                logger.info("Taking screenshot for debugging...")
                try:
                    page.screenshot(path=str(download_path / f"debug_custom_report_algo_{timestamp}.png"), full_page=True)
                except:
                    pass
                logger.warning("The script will continue and try to proceed with date configuration...")
            
            dismiss_popups(page)
            
            # STEP 6: Configure report settings (dates) if needed
            logger.info("Step 6/8: Configuring report settings (dates)...")
            
            dismiss_popups(page)
            
            # Fill date fields
            logger.debug("Setting date range...")
            start_date_set = try_selectors(page, SELECTORS["date_start"], "fill", start_date, timeout=3000)
            if start_date_set:
                logger.info(f"✓ Start date set: {start_date}")
            else:
                logger.warning("Could not set start date")
            
            end_date_set = try_selectors(page, SELECTORS["date_end"], "fill", end_date, timeout=3000)
            if end_date_set:
                logger.info(f"✓ End date set: {end_date}")
            else:
                logger.warning("Could not set end date")
            
            dismiss_popups(page)
            
            # STEP 7: Run the report and Download
            logger.info("Step 7/8: Running report and downloading...")
            
            # After configuring settings, click Run button to generate the report
            run_button_selectors = [
                'button:has-text("Run")',
                'button[type="submit"]',
                'button[aria-label*="Run" i]',
                'button.primary:has-text("Run")',
                'button.btn-primary:has-text("Run")',
            ]
            
            run_clicked = try_selectors(page, run_button_selectors, "click", timeout=5000)
            if run_clicked:
                logger.info("✓ Clicked Run button to generate report")
                page.wait_for_timeout(3000)  # Wait for report to generate
            else:
                logger.warning("Could not find Run button - report may already be generated")
            
            dismiss_popups(page)
            logger.debug("Setting up download event listener...")
            download_promise = page.wait_for_event("download", timeout=60000)
            
            download_clicked = try_selectors(page, SELECTORS["download_btn"], "click", timeout=5000)
            
            if not download_clicked:
                logger.warning("Could not click download button with standard selectors")
                logger.info("Trying alternative download methods...")
                
                # Try alternative download selectors
                alt_download = [
                    'button:has-text("Export")',
                    'button:has-text("CSV")',
                    'a:has-text("Download")',
                    '[download]',
                ]
                download_clicked = try_selectors(page, alt_download, "click", timeout=5000)
            
            if not download_clicked:
                logger.error("=" * 60)
                logger.error("✗ Could not trigger download")
                logger.error("=" * 60)
                logger.error("Please manually click the Download/Export button")
                logger.error("The script will wait 30 seconds for manual download...")
                logger.error("=" * 60)
                page.wait_for_timeout(30000)
            
            try:
                download = download_promise
                logger.info("✓ Download event received")
            except PlaywrightTimeout:
                logger.error("Download timeout - file download did not start")
                raise RuntimeError("Download timeout - file download did not start within 60 seconds")
            
            # STEP 8: Save downloaded file
            logger.info("Step 8/8: Saving file...")
            logger.debug(f"Saving to: {csv_path}")
            download.save_as(csv_path)
            
            if not csv_path.exists() or csv_path.stat().st_size == 0:
                raise RuntimeError("Download failed: file empty or missing")
            
            file_size = csv_path.stat().st_size
            logger.info("=" * 60)
            logger.info(f"✓ SUCCESS: {csv_path.name} ({file_size:,} bytes)")
            logger.info("=" * 60)
            
            return csv_path
            
        except Exception as e:
            logger.error(f"✗ FAILED: {e}")
            take_error_screenshot(page, download_path, timestamp)
            raise RuntimeError(f"Download failed: {e}") from e
        
        finally:
            browser.close()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Download IBKR Portfolio Analyst CSV")
    parser.add_argument("--username", help="IBKR username (or IBKR_USERNAME env)")
    parser.add_argument("--password", help="IBKR password (or IBKR_PASSWORD env)")
    parser.add_argument("--account-id", help="Account ID (or IBKR_ACCOUNT_ID env)")
    parser.add_argument("--start-date", help="Start date YYYY-MM-DD (default: 1 year ago)")
    parser.add_argument("--end-date", help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--download-dir", help="Download directory")
    parser.add_argument("--no-headless", action="store_true", help="Show browser (debug)")
    
    args = parser.parse_args()
    
    try:
        csv_path = download_pa_report(
            username=args.username,
            password=args.password,
            account_id=args.account_id,
            start_date=args.start_date,
            end_date=args.end_date,
            download_dir=args.download_dir,
            headless=not args.no_headless,
        )
        print(f"✓ Downloaded: {csv_path}")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
