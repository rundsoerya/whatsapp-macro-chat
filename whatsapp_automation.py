from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time


def wait_and_click(driver, wait, xpath, timeout=20):
    """Helper function to wait for element and click it safely"""
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # Small delay after scroll
        element.click()
        return True
    except ElementClickInterceptedException:
        # Try using JavaScript click if normal click fails
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"Failed to click element: {str(e)}")
            return False
    except Exception as e:
        print(f"Error clicking element: {str(e)}")
        return False


def send_whatsapp_message(contact_or_group_name, messages, delay_seconds=1, is_group=False):
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir=./User_Data')  # Keep session
        options.add_argument('--start-maximized')  # Start with maximized window
        options.add_argument('--disable-notifications')  # Disable notifications
        
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds for elements
        actions = ActionChains(driver)

        # Open WhatsApp Web
        driver.get('https://web.whatsapp.com')
        print('Please scan the QR code if not already logged in.')
        
        # Wait for the chat list to load
        chat_list = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]')))
        time.sleep(3)  # Additional wait for stability
        
        # Click on the search box
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
        search_box.clear()
        search_box.send_keys(contact_or_group_name)
        time.sleep(2)

        # Try to find and click the contact/group
        contact_xpath = f'//span[@title="{contact_or_group_name}"]'
        if not wait_and_click(driver, wait, contact_xpath):
            print(f"Could not find or click on {contact_or_group_name}")
            return

        time.sleep(2)

        # Find the message box
        message_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        
        # Send each message with delay
        for i, message in enumerate(messages, 1):
            message_box.click()
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            print(f'Message {i}/{len(messages)} sent to {contact_or_group_name}!')
            
            if i < len(messages):  # Don't wait after the last message
                time.sleep(delay_seconds)
        
    except TimeoutException:
        print("Error: Element not found within the specified time.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


if __name__ == '__main__':
    print("WhatsApp Message Sender")
    print("----------------------")
    recipient_type = input("Send to (1) Individual or (2) Group? Enter 1 or 2: ")
    name = input("Enter the contact/group name exactly as it appears in WhatsApp: ")
    
    # Get messages
    print("\nEnter your messages (type 'DONE' on a new line when finished):")
    messages = []
    while True:
        message = input("> ")
        if message.upper() == 'DONE':
            break
        messages.append(message)
    
    # Get delay
    while True:
        try:
            delay = float(input("\nEnter delay between messages in seconds (e.g., 1.0): "))
            if delay < 0.5:
                print("Delay must be at least 0.5 seconds to avoid detection")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    is_group = recipient_type == "2"
    send_whatsapp_message(name, messages, delay, is_group) 