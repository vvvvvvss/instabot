from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Function to log in to Instagram
def login_instagram(username, password):
    driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed and PATH configured
    driver.get("https://www.instagram.com/accounts/login/")

    # Wait for the username field to appear and then log in
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Click login
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait until the homepage loads after login
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Home']"))
    )

    return driver


# Function to get the followers
def get_followers(driver):
    driver.get("https://www.instagram.com/poloriod21/")
    time.sleep(5)  # Wait for the profile page to load

    # Wait for the followers link to appear and click on it
    try:
        followers_link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "followers"))
        )
        followers_link.click()
        time.sleep(9)  # Wait for the followers modal to load

        # Scroll the followers modal to get all followers
        followers_modal = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] ul"))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", followers_modal)

        follower_urls = []

        while True:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", followers_modal)
            time.sleep(5)  # Allow time for new followers to load
            new_height = driver.execute_script("return arguments[0].scrollHeight", followers_modal)
            if new_height == last_height:
                break
            last_height = new_height

        # Collect follower URLs (only first follower for now)
        followers = followers_modal.find_elements(By.CSS_SELECTOR, "li div div div a")
        for follower in followers[:1]:  # Limit to only 1 follower
            follower_urls.append(follower.get_attribute('href'))

        return follower_urls

    except Exception as e:
        print("Error while getting followers:", e)
        return []


# Function to like the latest post from one follower
def like_latest_post_from_one_follower(driver, follower_urls):
    if not follower_urls:
        print("No followers found to like posts.")
        return

    # Visit the first follower's page
    follower_url = follower_urls[0]
    driver.get(follower_url)
    time.sleep(3)  # Wait for the page to load

    # Find and like the most recent post
    try:
        post = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article div div div a"))
        )
        post.click()
        time.sleep(2)

        like_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@aria-label='Like']"))
        )
        like_button.click()
        print("Liked the latest post from", follower_url)

    except Exception as e:
        print("Could not like post for follower:", follower_url, e)


# Function to send automated message if you don't reply within 5 minutes
def send_automated_message(driver, recipient, message="I'm away at the moment, will get back to you soon."):
    driver.get(f"https://www.instagram.com/direct/inbox/")
    time.sleep(10) # Allow time for the inbox to load

    try:
        # Find the recipient's conversation
        user_convo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, recipient))
        )
        user_convo.click()

        # Check if there are any new messages from the recipient
        last_message_time = time.time()

        # Wait for 5 minutes to check for reply
        time.sleep(300)  # 5 minutes wait

        # If no reply, send the automated message
        current_time = time.time()
        if current_time - last_message_time >= 300:
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            message_box.send_keys(message)
            message_box.send_keys("hi")  # Send the message

            print("Sent automated message to", recipient)

    except Exception as e:
        print("Could not send message to", recipient, e)


# Main function to run the bot
def main():
    username = "poloriod21"  # Replace with your Instagram username
    password = "xxxxxxxx"  # Replace with your Instagram password
    recipient = "varsha_shubhashri"  # Replace with the username of the recipient for the automated message

    driver = login_instagram(username,password)

    # Step 1: Like one post from one follower
    follower_urls = get_followers(driver)  # Get the list of followers
    like_latest_post_from_one_follower(driver, follower_urls)  # Like one post from the first follower

    # Step 2: Send an automated message if no reply in 5 minutes
    send_automated_message(driver, recipient)

    driver.quit()  # Close the browser when done


if __name__ == "__main__":
    main()
