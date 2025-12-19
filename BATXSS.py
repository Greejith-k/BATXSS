from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException
import time
from colorama import Fore, Style, init

# Initialize colorama
init()


banner = rf"""
{Fore.RED}
  ____    _  _______  ______ ____  
 | __ )  / \|_   _\ \/ / ___/ ___| 
 |  _ \ / _ \ | |  \  /\___ \___ \ 
 | |_) / ___ \| |  /  \ ___) |__) |
 |____/_/   \_\_| /_/\_\____/____/ 
                                   
{Style.RESET_ALL}
{Fore.GREEN}               Created by Greejith K
   LinkedIn: https://in.linkedin.com/in/greejith-k-64b28a241
{Style.RESET_ALL}
"""

print(banner)


def setup_driver():
    """Configure headless Chrome browser"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_xss_with_browser(full_url, payload, timeout=5):
    """
    Test for reflected XSS vulnerability with actual browser rendering

    Args:
        full_url (str): Fully constructed URL with payload
        payload (str): XSS payload to test
        timeout (int): Seconds to wait for alert

    Returns:
        tuple: (reflected, executed)
    """
    driver = setup_driver()
    try:
        print(f"[*] Testing payload: {payload}")

        # Navigate to URL
        driver.get(full_url)
        page_source = driver.page_source

        # Check for reflection
        reflected = payload in page_source
        if reflected:
            print(Fore.BLUE + f"[!] Reflection detected for payload: {payload}" + Style.RESET_ALL)

        # Check for alert presence
        executed = False
        try:
            alert = driver.switch_to.alert
            print(Fore.RED + f"[!] XSS CONFIRMED: Alert detected for payload: {payload}")
            print(f"    Alert text: {alert.text}" + Style.RESET_ALL)
            alert.accept()
            executed = True
        except UnexpectedAlertPresentException:
            try:
                alert = driver.switch_to.alert
                print(Fore.RED + f"[!] XSS CONFIRMED: Alert detected for payload: {payload}")
                print(f"    Alert text: {alert.text}" + Style.RESET_ALL)
                alert.accept()
                executed = True
            except:
                pass
        except:
            if reflected:
                print(Fore.BLUE + "[*] Payload reflected but didn't execute" + Style.RESET_ALL)
            else:
                print("[*] No reflection or execution detected")

        return (reflected, executed)

    except WebDriverException as e:
        if "unexpected alert open" in str(e):
            print(Fore.RED + f"[!] XSS CONFIRMED: Alert detected for payload: {payload}" + Style.RESET_ALL)
            return (True, True)
        else:
            print(f"[!] Browser error: {str(e)}")
            return (False, False)
    finally:
        try:
            driver.quit()
        except:
            pass

def load_wordlist(wordlist_path):
    """Load XSS payloads from a file"""
    with open(wordlist_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    print("NextGen XSS Tester")

    # Get user inputs
    base_url_template = input("Enter target URL with %s as the injection point (e.g., https://example.com/search?q=%s): ").strip()
    if "%s" not in base_url_template:
        print(Fore.RED + "[!] Error: URL must contain '%s' as injection point." + Style.RESET_ALL)
        exit(1)

    wordlist_path = input("Enter path to payload wordlist: ").strip()

    try:
        payloads = load_wordlist(wordlist_path)
        print(f"\nLoaded {len(payloads)} payloads from wordlist\n")

        vulnerable_payloads = []

        for payload in payloads:
            full_url = base_url_template % payload
            reflected, executed = test_xss_with_browser(full_url, payload)
            if executed:
                vulnerable_payloads.append((payload, "EXECUTED"))
            elif reflected:
                vulnerable_payloads.append((payload, "REFLECTED"))

            time.sleep(1)

        # Print summary
        print("\n" + "="*50)
        print(Fore.RED + "Vulnerable Payloads Summary:" + Style.RESET_ALL)
        for payload, status in vulnerable_payloads:
            if status == "EXECUTED":
                print(Fore.RED + f"[EXECUTED] {payload}" + Style.RESET_ALL)
            else:
                print(Fore.BLUE + f"[REFLECTED] {payload}" + Style.RESET_ALL)

    except FileNotFoundError:
        print(Fore.RED + f"[!] Error: Wordlist file not found at {wordlist_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[!] Unexpected error: {str(e)}" + Style.RESET_ALL)
