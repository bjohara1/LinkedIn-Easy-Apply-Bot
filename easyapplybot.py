from __future__ import annotations

import json
import csv
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import getpass
from pathlib import Path

import pandas as pd
import pyautogui
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.service import Service as ChromeService
import webdriver_manager.chrome as ChromeDriverManager
ChromeDriverManager = ChromeDriverManager.ChromeDriverManager


log = logging.getLogger(__name__)


def setupLogger() -> None:
    dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")

    if not os.path.isdir('./logs'):
        os.mkdir('./logs')

    # TODO need to check if there is a log dir available or not
    logging.basicConfig(filename=('./logs/' + str(dt) + 'applyJobs.log'), filemode='w',
                        format='%(asctime)s::%(name)s::%(levelname)s::%(message)s', datefmt='./logs/%d-%b-%y %H:%M:%S')
    log.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
    c_handler.setFormatter(c_format)
    log.addHandler(c_handler)


class EasyApplyBot:
    setupLogger()
    # MAX_SEARCH_TIME is 10 hours by default, feel free to modify it
    MAX_SEARCH_TIME = 60 * 60

    def __init__(self,
                 username,
                 password,
                 phone_number,
                 # profile_path,
                 salary,
                 rate,
                 uploads={},
                 filename='output.csv',
                 blacklist=[],
                 blackListTitles=[],
                 experience_level=[],
                 years_of_experience=8,
                 interactive_mode=False
                 ) -> None:

        log.info("Welcome to Easy Apply Bot")
        dirpath: str = os.getcwd()
        log.info("current directory is : " + dirpath)
        log.info("Please wait while we prepare the bot for you")
        if experience_level:
            experience_levels = {
                1: "Entry level",
                2: "Associate",
                3: "Mid-Senior level",
                4: "Director",
                5: "Executive",
                6: "Internship"
            }
            applied_levels = [experience_levels[level] for level in experience_level]
            log.info("Applying for experience level roles: " + ", ".join(applied_levels))
        else:
            log.info("Applying for all experience levels")
        

        self.uploads = uploads
        self.salary = salary
        self.rate = rate
        self.years_of_experience = years_of_experience
        self.interactive_mode = interactive_mode
        # self.profile_path = profile_path
        past_ids: list | None = self.get_appliedIDs(filename)
        self.appliedJobIDs: list = past_ids if past_ids != None else []
        self.filename: str = filename
        self.options = self.browser_options()
        self.browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        self.wait = WebDriverWait(self.browser, 30)
        self.blacklist = blacklist
        self.blackListTitles = blackListTitles
        self.start_linkedin(username, password)
        self.phone_number = phone_number
        self.experience_level = experience_level


        self.locator = {
            "next": (By.CSS_SELECTOR, "button[aria-label='Continue to next step']"),
            "review": (By.CSS_SELECTOR, "button[aria-label='Review your application']"),
            "submit": (By.CSS_SELECTOR, "button[aria-label='Submit application']"),
            "error": (By.CLASS_NAME, "artdeco-inline-feedback__message"),
            "upload_resume": (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-resume')]"),
            "upload_cv": (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-cover-letter')]"),
            "follow": (By.CSS_SELECTOR, "label[for='follow-company-checkbox']"),
            "upload": (By.NAME, "file"),
            "search": (By.CLASS_NAME, "jobs-search-results-list"),
            "links": ("xpath", '//div[@data-job-id]'),
            "fields": (By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"),
            "radio_select": (By.CSS_SELECTOR, "input[type='radio']"), #need to append [value={}].format(answer)
            "multi_select": (By.XPATH, "//*[contains(@id, 'text-entity-list-form-component')]"),
            "text_select": (By.CLASS_NAME, "artdeco-text-input--input"),
            "2fa_oneClick": (By.ID, 'reset-password-submit-button'),
            "easy_apply_button": (By.XPATH, '//button[contains(@class, "jobs-apply-button")]')

        }

        #initialize questions and answers file
        self.qa_file = Path("qa.csv")
        self.answers = {}

        #if qa file does not exist, create it
        if self.qa_file.is_file():
            df = pd.read_csv(self.qa_file)
            for index, row in df.iterrows():
                self.answers[row['Question']] = row['Answer']
        #if qa file does exist, load it
        else:
            df = pd.DataFrame(columns=["Question", "Answer"])
            df.to_csv(self.qa_file, index=False, encoding='utf-8')

        # Load custom answers from YAML file
        self.user_answers = []
        try:
            with open("questions.yaml", 'r') as stream:
                self.user_answers = yaml.safe_load(stream)
            log.info("Loaded custom answers from questions.yaml")
        except FileNotFoundError:
            log.info("questions.yaml not found, will use default answering logic.")
        except yaml.YAMLError as exc:
            log.error(f"Error parsing questions.yaml: {exc}")

        # Initialize unanswered questions tracking
        self.unanswered_questions_file = Path("unanswered_questions.yaml")
        self.unanswered_questions = set()
        if not self.unanswered_questions_file.exists():
            with open(self.unanswered_questions_file, 'w') as f:
                f.write("# Unanswered Questions\n")
                f.write("# Review and add appropriate keywords and answers below\n")
                f.write("# Then copy them to questions.yaml for the bot to use\n\n")


    def get_appliedIDs(self, filename) -> list | None:
        try:
            df = pd.read_csv(filename,
                             header=None,
                             names=['timestamp', 'jobID', 'job', 'company', 'attempted', 'result'],
                             lineterminator='\n',
                             encoding='utf-8')

            df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d %H:%M:%S")
            df = df[df['timestamp'] > (datetime.now() - timedelta(days=2))]
            jobIDs: list = list(df.jobID)
            log.info(f"{len(jobIDs)} jobIDs found")
            return jobIDs
        except Exception as e:
            log.info(str(e) + "   jobIDs could not be loaded from CSV {}".format(filename))
            return None

    def browser_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        #options.add_argument(r'--remote-debugging-port=9222')
        #options.add_argument(r'--profile-directory=Person 1')

        # Disable webdriver flags or you will be easily detectable
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Load user profile
        #options.add_argument(r"--user-data-dir={}".format(self.profile_path))
        return options

    def start_linkedin(self, username, password) -> None:
        log.info("Logging in.....Please wait :)  ")
        self.browser.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        try:
            # Wait for username field to be present
            user_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            user_field.send_keys(username)
            user_field.send_keys(Keys.TAB)

            # Find password field
            pw_field = self.browser.find_element("id","password")
            pw_field.send_keys(password)
            
            # Try multiple possible login button selectors
            login_button = None
            possible_selectors = [
                '//*[@id="organic-div"]/form/div[3]/button',
                '//button[@type="submit"]',
                '//button[contains(text(), "Sign in")]',
                '//button[contains(text(), "Sign")]',
                '//input[@type="submit"]'
            ]
            
            for selector in possible_selectors:
                try:
                    login_button = self.browser.find_element("xpath", selector)
                    if login_button:
                        log.info(f"Found login button with selector: {selector}")
                        break
                except:
                    continue
            
            if login_button:
                login_button.click()
                log.info("Login button clicked successfully")
            else:
                # If no button found, try pressing Enter
                pw_field.send_keys(Keys.RETURN)
                log.info("No login button found, pressed Enter instead")

            # Smart wait: Check for successful login or authentication challenges
            log.info("Waiting for login to complete...")
            for _ in range(30):  # Check for up to 30 seconds
                time.sleep(1)
                current_url = self.browser.current_url
                if "feed" in current_url or "mynetwork" in current_url:
                    log.info("Login successful!")
                    break
                elif "checkpoint" in current_url or "challenge" in current_url:
                    log.info("Additional authentication required. Please complete manually.")
                    log.info("You have 60 seconds to complete authentication...")
                    time.sleep(60)
                    break
            
            # Check if login was successful
            if "feed" in self.browser.current_url or "mynetwork" in self.browser.current_url:
                log.info("Successfully logged into LinkedIn!")
            else:
                log.info("Login may have failed. Current URL: " + self.browser.current_url)
                
        except TimeoutException:
            log.info("TimeoutException! Username/password field or login button not found")
        except Exception as e:
            log.info(f"Login error: {str(e)}")
            log.info("Please check your credentials and try again.")

    def fill_data(self) -> None:
        self.browser.set_window_size(1, 1)
        self.browser.set_window_position(2000, 2000)

    def start_apply(self, positions, locations) -> None:
        start: float = time.time()
        self.fill_data()
        self.positions = positions
        self.locations = locations
        combos: list = []
        while len(combos) < len(positions) * len(locations):
            position = positions[random.randint(0, len(positions) - 1)]
            location = locations[random.randint(0, len(locations) - 1)]
            combo: tuple = (position, location)
            if combo not in combos:
                combos.append(combo)
                log.info(f"Applying to {position}: {location}")
                location = "&location=" + location
                self.applications_loop(position, location)
            if len(combos) > 500:
                break

    # self.finish_apply() --> this does seem to cause more harm than good, since it closes the browser which we usually don't want, other conditions will stop the loop and just break out

    def applications_loop(self, position, location):

        count_application = 0
        count_job = 0
        jobs_per_page = 0
        start_time: float = time.time()

        log.info("Looking for jobs.. Please wait..")

        self.browser.set_window_position(1, 1)
        self.browser.maximize_window()
        self.browser, _ = self.next_jobs_page(position, location, jobs_per_page, experience_level=self.experience_level)
        log.info("Looking for jobs.. Please wait..")

        while time.time() - start_time < self.MAX_SEARCH_TIME:
            try:
                log.info(f"{(self.MAX_SEARCH_TIME - (time.time() - start_time)) // 60} minutes left in this search")

                # sleep to make sure everything loads, add random to make us look human.
                randoTime: float = random.uniform(1.5, 2.9)
                log.debug(f"Sleeping for {round(randoTime, 1)}")
                #time.sleep(randoTime)
                self.load_page(sleep=0.1)

                # LinkedIn displays the search results in a scrollable <div> on the left side, we have to scroll to its bottom

                # scroll to bottom

                if self.is_present(self.locator["search"]):
                    scrollresults = self.get_elements("search")
                    #     self.browser.find_element(By.CLASS_NAME,
                    #     "jobs-search-results-list"
                    # )
                    # Selenium only detects visible elements; if we scroll to the bottom too fast, only 8-9 results will be loaded into IDs list
                    for i in range(300, 3000, 100):
                        self.browser.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresults[0])
                    scrollresults = self.get_elements("search")
                    #time.sleep(1)

                # get job links, (the following are actually the job card objects)
                if self.is_present(self.locator["links"]):
                    links = self.get_elements("links")
                # links = self.browser.find_elements("xpath",
                #     '//div[@data-job-id]'
                # )

                    jobIDs = {} #{Job id: processed_status}
                    job_cards = {} #{Job id: card_element} - Store card elements for Easy Apply

                    # children selector is the container of the job cards on the left
                    for link in links:
                            if 'Applied' not in link.text: #checking if applied already
                                # Extract job title and company from card
                                lines = link.text.splitlines() if link.text else []
                                job_title = lines[0] if len(lines) > 0 else ""
                                company = lines[1] if len(lines) > 1 else ""

                                # Check if company is blacklisted
                                if any(blacklisted.lower() in company.lower() for blacklisted in self.blacklist):
                                    log.info(f"Skipping blacklisted company: '{company}'")
                                    continue

                                # Check if job title contains blacklisted keywords
                                if any(blacklisted.lower() in job_title.lower() for blacklisted in self.blackListTitles):
                                    log.info(f"Skipping blacklisted job title: '{job_title}'")
                                    continue

                                # Enhanced relevance check with scoring
                                relevance_score = self.calculate_job_relevance(job_title)

                                if relevance_score > 0:
                                    jobID = link.get_attribute("data-job-id")
                                    if jobID == "search":
                                        log.debug("Job ID not found, search keyword found instead? {}".format(link.text))
                                        continue
                                    else:
                                        log.info(f"Job matched (score: {relevance_score}): '{job_title}' at '{company}'")
                                        jobIDs[jobID] = "To be processed"
                                        job_cards[jobID] = link  # Store the card element
                                else:
                                    log.debug(f"Skipping low-relevance job: '{job_title}'")
                    if len(jobIDs) > 0:
                        self.apply_loop(jobIDs, job_cards)
                    self.browser, jobs_per_page = self.next_jobs_page(position,
                                                                      location,
                                                                      jobs_per_page, 
                                                                      experience_level=self.experience_level)
                else:
                    self.browser, jobs_per_page = self.next_jobs_page(position,
                                                                      location,
                                                                      jobs_per_page, 
                                                                      experience_level=self.experience_level)


            except Exception as e:
                print(e)
    def calculate_job_relevance(self, job_title):
        """
        Calculate relevance score for a job title based on position keywords.
        Returns: score > 0 if relevant, 0 if not relevant
        """
        job_title_lower = job_title.lower()
        score = 0

        # Exclude these irrelevant job types immediately (score = 0)
        irrelevant_keywords = [
            'intern', 'internship',  # Unless specifically searching for these
            'entry level data entry', 'data entry clerk',  # Not analytics
            'senior manager', 'director', 'vp ', 'vice president',  # Too senior unless specified
            'recruiter', 'recruitment',  # Not technical roles
            'sales', 'account executive',  # Not technical
            'customer service', 'customer support',
            'administrative', 'secretary', 'clerk'
        ]

        # Check for explicitly irrelevant keywords first
        for irrelevant in irrelevant_keywords:
            if irrelevant in job_title_lower:
                # But allow if user is explicitly searching for them
                if not any(pos.lower() in irrelevant for pos in self.positions):
                    log.debug(f"Excluding due to irrelevant keyword '{irrelevant}': {job_title}")
                    return 0

        # Positive scoring: Match position keywords
        for position in self.positions:
            position_lower = position.lower()

            # Exact match = high score
            if position_lower == job_title_lower:
                score += 100
                continue

            # Position keyword is in the title
            if position_lower in job_title_lower:
                score += 50

                # Bonus: Check for related terms that indicate good match
                related_terms = {
                    'data': ['analyst', 'scientist', 'engineer', 'analytics'],
                    'analytics': ['analyst', 'engineer', 'specialist'],
                    'analyst': ['data', 'business', 'analytics'],
                    'engineer': ['data', 'analytics', 'software', 'machine learning'],
                    'scientist': ['data', 'machine learning', 'research']
                }

                if position_lower in related_terms:
                    for related_term in related_terms[position_lower]:
                        if related_term in job_title_lower:
                            score += 20  # Bonus for related terms

        # Fuzzy matching for partial keyword matches
        if score == 0:
            for position in self.positions:
                similarity = SequenceMatcher(None, position.lower(), job_title_lower).ratio()
                if similarity > 0.6:  # 60% similarity
                    score += int(similarity * 30)

        return score

    def apply_loop(self, jobIDs, job_cards):
        for jobID in jobIDs:
            if jobIDs[jobID] == "To be processed":
                job_card = job_cards.get(jobID)  # Get the job card element
                applied = self.apply_to_job(jobID, job_card)
                if applied:
                    log.info(f"Applied to {jobID}")
                else:
                    log.info(f"Failed to apply to {jobID}")
                jobIDs[jobID] = applied  # Fixed: was == (comparison), now = (assignment)

    def apply_to_job(self, jobID, job_card=None):
        """
        Apply to a job directly from the search results
        Args:
            jobID: The LinkedIn job ID
            job_card: The WebElement representing the job card in search results
        """
        # Find Easy Apply button in the job card (faster - no page navigation!)
        button = self.get_easy_apply_button_from_card(job_card, jobID)

        # Get job title for logging
        try:
            job_title = job_card.text.splitlines()[0] if job_card and job_card.text else "Unknown"
        except:
            job_title = "Unknown"

        # word filter to skip positions not wanted
        if button is not False:
            if any(word.lower() in job_title.lower() for word in self.blackListTitles):
                log.info('Skipping this application, a blacklisted keyword was found in the job position')
                string_easy = "* Contains blacklisted keyword"
                result = False
            else:
                string_easy = "* has Easy Apply Button"
                log.info(f"Clicking Easy Apply button for: {job_title}")
                try:
                    button.click()
                    time.sleep(1)  # Wait for modal to open
                    self.fill_out_fields()
                    result: bool = self.send_resume()
                    if result:
                        string_easy = "*Applied: Sent Resume"
                    else:
                        string_easy = "*Did not apply: Failed to send Resume"
                except Exception as e:
                    log.error(f"Error clicking Easy Apply button: {e}")
                    string_easy = "*Error clicking button"
                    result = False
        else:
            log.info(f"No Easy Apply button for: {job_title}")
            string_easy = "* Doesn't have Easy Apply Button"
            result = False

        log.info(f"\nPosition {jobID}: {job_title}\n {string_easy}\n")

        self.write_to_file(button, jobID, job_title, result)
        return result

    def write_to_file(self, button, jobID, job_title, result) -> None:
        """Write application attempt to CSV file"""
        timestamp: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attempted: bool = False if button == False else True

        # job_title might be in format "Job Title\nCompany Name" or just "Job Title"
        lines = job_title.split('\n') if job_title else ['Unknown']
        job = lines[0] if len(lines) > 0 else "Unknown"
        company = lines[1] if len(lines) > 1 else "Unknown"

        toWrite: list = [timestamp, jobID, job, company, attempted, result]
        with open(self.filename, 'a+') as f:
            writer = csv.writer(f)
            writer.writerow(toWrite)

    def get_easy_apply_button_from_card(self, job_card, jobID):
        """
        Find Easy Apply button after clicking on a job card in search results.
        The button appears in the job details panel on the right side, not within the card itself.
        """
        if not job_card:
            log.warning(f"No job card provided for {jobID}")
            return False

        try:
            # Step 1: Click the job card to load the job details panel
            try:
                self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
                time.sleep(0.3)
                job_card.click()
                log.debug(f"Clicked job card for job {jobID}")
                time.sleep(1.5)  # Wait longer for the job details panel to fully load
            except Exception as e:
                log.error(f"Failed to click job card: {e}")
                return False

            # Step 2: Look for Easy Apply button in the job details panel (right side of page)
            # The button appears OUTSIDE the job card, in the job details section
            
            # Strategy 1: Find by ID (most specific)
            # Try both possible IDs that LinkedIn uses
            for button_id in ['jobs-apply-button', 'jobs-apply-button-id']:
                try:
                    button = self.browser.find_element(By.ID, button_id)
                    if button.is_displayed() and button.is_enabled():
                        log.info(f"✓ Found Easy Apply button by ID '{button_id}' for job {jobID}")
                        return button
                except:
                    log.debug(f"ID '{button_id}' not found")
                    continue

            # Strategy 2: Find by class name (from your HTML)
            try:
                buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button.jobs-apply-button')
                log.debug(f"Found {len(buttons)} buttons with class 'jobs-apply-button'")
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            # Verify this button is for the correct job
                            button_job_id = button.get_attribute('data-job-id')
                            aria_label = button.get_attribute('aria-label') or ''
                            log.debug(f"Button data-job-id: {button_job_id}, aria-label: {aria_label[:50]}...")
                            
                            # Match by job ID if available, otherwise just take the visible button
                            if button_job_id == str(jobID) or not button_job_id:
                                log.info(f"✓ Found Easy Apply button for job {jobID}")
                                return button
                    except Exception as e:
                        log.debug(f"Button check failed: {e}")
                        continue
            except Exception as e:
                log.debug(f"Strategy 2 (class) failed: {e}")

            # Strategy 3: Find by aria-label containing "Easy Apply"
            try:
                buttons = self.browser.find_elements(By.XPATH, '//button[contains(@aria-label, "Easy Apply")]')
                log.debug(f"Found {len(buttons)} buttons with 'Easy Apply' in aria-label")
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            button_job_id = button.get_attribute('data-job-id')
                            if button_job_id == str(jobID) or not button_job_id:
                                log.info(f"✓ Found Easy Apply button by aria-label for job {jobID}")
                                return button
                    except:
                        continue
            except Exception as e:
                log.debug(f"Strategy 3 (aria-label) failed: {e}")

            # Strategy 4: Find button with text "Easy Apply"
            try:
                buttons = self.browser.find_elements(By.XPATH, '//button[contains(., "Easy Apply")]')
                log.debug(f"Found {len(buttons)} buttons with 'Easy Apply' text")
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.strip()
                            if 'easy apply' in button_text.lower():
                                log.info(f"✓ Found Easy Apply button by text for job {jobID}")
                                return button
                    except:
                        continue
            except Exception as e:
                log.debug(f"Strategy 4 (text) failed: {e}")

            # Strategy 5: Look for any artdeco-button with primary styling that might be Easy Apply
            try:
                buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button.artdeco-button--primary')
                log.debug(f"Found {len(buttons)} primary buttons")
                for button in buttons:
                    try:
                        button_text = button.text.strip().lower()
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        if 'easy apply' in button_text or 'easy apply' in aria_label:
                            if button.is_displayed() and button.is_enabled():
                                log.info(f"✓ Found Easy Apply button (primary button) for job {jobID}")
                                return button
                    except:
                        continue
            except Exception as e:
                log.debug(f"Strategy 5 (primary button) failed: {e}")

            log.info(f"No Easy Apply button found for job {jobID} - job may not have Easy Apply option")
            return False

        except Exception as e:
            log.error(f"Error finding Easy Apply button for job {jobID}: {e}")
            return False

    def get_job_page(self, jobID):
        """Navigate to a specific job page"""
        job: str = 'https://www.linkedin.com/jobs/view/' + str(jobID)
        log.info(f"Navigating to job: {job}")
        self.browser.get(job)

        # Give the page a moment to load before scrolling
        time.sleep(0.5)

        # Scroll to load content, but less aggressively
        for i in range(0, 2000, 500):
            self.browser.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.1)

        # Scroll back to top where the Easy Apply button usually is
        self.browser.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)

        return self.browser.page_source

    def get_easy_apply_button(self):
        """Find and return the Easy Apply button with improved detection"""
        EasyApplyButton = False

        try:
            # Wait a bit for the page to fully load
            time.sleep(1.5)

            # Strategy 1: Try the most specific CSS selector first (this is most reliable)
            log.debug("Trying CSS selector: button.jobs-apply-button")
            try:
                buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button.jobs-apply-button')
                log.debug(f"Found {len(buttons)} buttons with class 'jobs-apply-button'")

                for button in buttons:
                    # Log all attributes to debug
                    button_text = button.text.strip()
                    aria_label = button.get_attribute('aria-label') or ''
                    button_class = button.get_attribute('class') or ''

                    log.debug(f"Button - Text: '{button_text}', aria-label: '{aria_label}', class: '{button_class}'")

                    # Check if this looks like the Easy Apply button
                    # Accept if: has the right class OR text/aria-label contains "Easy Apply"
                    if (button.is_displayed() and button.is_enabled() and
                        ('jobs-apply-button' in button_class or
                         'easy apply' in button_text.lower() or
                         'easy apply' in aria_label.lower())):
                        try:
                            self.wait.until(EC.element_to_be_clickable(button))
                            log.info(f"✓ Found clickable Easy Apply button! (Text: '{button_text}')")
                            return button
                        except:
                            log.debug("Button found but not clickable yet, trying next...")
                            continue
            except Exception as e:
                log.debug(f"CSS selector failed: {str(e)}")

            # Strategy 2: Try XPath with text contains
            log.debug("Trying XPath with text contains")
            try:
                buttons = self.browser.find_elements(By.XPATH, '//button[contains(., "Easy Apply")]')
                log.debug(f"Found {len(buttons)} buttons with 'Easy Apply' text")

                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        try:
                            self.wait.until(EC.element_to_be_clickable(button))
                            log.info(f"✓ Found clickable Easy Apply button via XPath!")
                            return button
                        except:
                            continue
            except Exception as e:
                log.debug(f"XPath selector failed: {str(e)}")

            # Strategy 3: Try aria-label
            log.debug("Trying XPath with aria-label")
            try:
                buttons = self.browser.find_elements(By.XPATH, '//button[contains(@aria-label, "Easy Apply")]')
                log.debug(f"Found {len(buttons)} buttons with 'Easy Apply' aria-label")

                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        try:
                            self.wait.until(EC.element_to_be_clickable(button))
                            log.info(f"✓ Found clickable Easy Apply button via aria-label!")
                            return button
                        except:
                            continue
            except Exception as e:
                log.debug(f"Aria-label selector failed: {str(e)}")

            # If we get here, no button was found
            log.info("No Easy Apply button found on this job")

        except Exception as e:
            log.error(f"Error in get_easy_apply_button: {e}")

        return EasyApplyButton

    def close_easy_apply_modal(self):
        """Close the Easy Apply modal if it's open"""
        try:
            # First, check for and handle "Discard" confirmation dialog
            try:
                discard_button_selectors = [
                    (By.XPATH, '//button[@data-test-dialog-primary-btn]'),  # "Discard" button
                    (By.XPATH, '//button[contains(text(), "Discard")]'),
                    (By.XPATH, '//button[contains(@aria-label, "Discard")]'),
                ]

                for selector in discard_button_selectors:
                    try:
                        discard_btn = self.browser.find_element(selector[0], selector[1])
                        if discard_btn.is_displayed():
                            discard_btn.click()
                            log.debug("Clicked Discard button on confirmation dialog")
                            time.sleep(0.5)
                            break
                    except:
                        continue
            except:
                pass

            # Then try to close the main Easy Apply modal
            close_button_selectors = [
                (By.CSS_SELECTOR, 'button[aria-label="Dismiss"]'),
                (By.CSS_SELECTOR, 'button[data-test-modal-close-btn]'),
                (By.XPATH, '//button[contains(@aria-label, "Dismiss")]'),
                (By.XPATH, '//button[contains(@class, "artdeco-modal__dismiss")]'),
                (By.CSS_SELECTOR, 'button.artdeco-modal__dismiss'),
            ]

            for selector in close_button_selectors:
                try:
                    close_button = self.browser.find_element(selector[0], selector[1])
                    if close_button.is_displayed():
                        close_button.click()
                        log.debug("Closed Easy Apply modal")
                        time.sleep(0.5)

                        # After clicking X, check again for discard dialog
                        try:
                            discard_btn = self.browser.find_element(By.XPATH, '//button[@data-test-dialog-primary-btn]')
                            if discard_btn.is_displayed():
                                discard_btn.click()
                                log.debug("Clicked Discard after closing modal")
                                time.sleep(0.5)
                        except:
                            pass

                        return True
                except:
                    continue

            # If no close button found, try pressing ESC key
            try:
                ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
                log.debug("Closed modal with ESC key")
                time.sleep(0.5)

                # Check for discard dialog after ESC
                try:
                    discard_btn = self.browser.find_element(By.XPATH, '//button[@data-test-dialog-primary-btn]')
                    if discard_btn.is_displayed():
                        discard_btn.click()
                        log.debug("Clicked Discard after ESC")
                        time.sleep(0.5)
                except:
                    pass

                return True
            except:
                pass

            log.debug("No modal to close or already closed")
            return False

        except Exception as e:
            log.debug(f"Error closing modal: {e}")
            return False

    def fill_out_fields(self):
        fields = self.browser.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
        for field in fields:

            if "Mobile phone number" in field.text:
                field_input = field.find_element(By.TAG_NAME, "input")
                field_input.clear()
                field_input.send_keys(self.phone_number)


        return


    def get_elements(self, type) -> list:
        elements = []
        element = self.locator[type]
        if self.is_present(element):
            elements = self.browser.find_elements(element[0], element[1])
        return elements

    def is_present(self, locator):
        return len(self.browser.find_elements(locator[0],
                                              locator[1])) > 0

    def send_resume(self) -> bool:
        def is_present(button_locator) -> bool:
            return len(self.browser.find_elements(button_locator[0],
                                                  button_locator[1])) > 0

        try:
            #time.sleep(random.uniform(1.5, 2.5))
            next_locator = (By.CSS_SELECTOR,
                            "button[aria-label='Continue to next step']")
            review_locator = (By.CSS_SELECTOR,
                              "button[aria-label='Review your application']")
            submit_locator = (By.CSS_SELECTOR,
                              "button[aria-label='Submit application']")
            error_locator = (By.CLASS_NAME,"artdeco-inline-feedback__message")
            upload_resume_locator = (By.XPATH, '//span[text()="Upload resume"]')
            upload_cv_locator = (By.XPATH, '//span[text()="Upload cover letter"]')
            # WebElement upload_locator = self.browser.find_element(By.NAME, "file")
            follow_locator = (By.CSS_SELECTOR, "label[for='follow-company-checkbox']")

            submitted = False
            loop = 0
            while loop < 2:
                time.sleep(0.3)  # Brief wait for form elements
                # Upload resume
                if is_present(upload_resume_locator):
                    log.info("Resume upload section detected")
                    resume_path = self.uploads.get("Resume")

                    if not resume_path:
                        log.error("Resume path not configured in config.yaml")
                    elif not os.path.exists(resume_path):
                        log.error(f"Resume file not found at: {resume_path}")
                    else:
                        log.info(f"Attempting to upload resume from: {resume_path}")

                        # Try multiple strategies to find upload element
                        resume_uploaded = False
                        upload_strategies = [
                            (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-resume')]"),
                            (By.XPATH, "//input[@type='file' and contains(@id, 'resume')]"),
                            (By.XPATH, "//input[@type='file'][contains(@name, 'resume')]"),
                            (By.CSS_SELECTOR, "input[type='file'][id*='resume']"),
                        ]

                        for strategy in upload_strategies:
                            try:
                                resume_locator = self.browser.find_element(strategy[0], strategy[1])
                                log.debug(f"Found resume upload element using: {strategy}")
                                resume_locator.send_keys(resume_path)
                                log.info("✓ Resume uploaded successfully")
                                resume_uploaded = True
                                break
                            except Exception as e:
                                log.debug(f"Strategy {strategy} failed: {e}")
                                continue

                        if not resume_uploaded:
                            log.error(f"Failed to upload resume - could not find upload element")
                            log.error("LinkedIn may use a cached document from your profile instead")

                # Upload cover letter if possible
                if is_present(upload_cv_locator):
                    log.info("Cover letter upload section detected")
                    cv_path = self.uploads.get("Cover Letter")

                    if not cv_path:
                        log.warning("Cover letter path not configured in config.yaml")
                    elif not os.path.exists(cv_path):
                        log.error(f"Cover letter file not found at: {cv_path}")
                    else:
                        log.info(f"Attempting to upload cover letter from: {cv_path}")
                        try:
                            cv_locator = self.browser.find_element(By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-cover-letter')]")
                            cv_locator.send_keys(cv_path)
                            log.info("✓ Cover letter uploaded successfully")
                        except Exception as e:
                            log.error(f"Failed to upload cover letter: {e}")

                    #time.sleep(random.uniform(4.5, 6.5))
                elif len(self.get_elements("follow")) > 0:
                    elements = self.get_elements("follow")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()

                if len(self.get_elements("submit")) > 0:
                    elements = self.get_elements("submit")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()
                        log.info("Application Submitted")
                        submitted = True
                        break

                elif len(self.get_elements("error")) > 0:
                    elements = self.get_elements("error")
                    if "application was sent" in self.browser.page_source:
                        log.info("Application Submitted")
                        submitted = True
                        break
                    elif len(elements) > 0:
                        retry_count = 0
                        while len(elements) > 0 and retry_count < 3:
                            log.info("Please answer the questions, waiting 2 seconds...")
                            time.sleep(2)  # Reduced from 5s to 2s
                            elements = self.get_elements("error")
                            retry_count += 1

                            for element in elements:
                                should_continue = self.process_questions()
                                # If user chose to discard, break out of retry loop
                                if should_continue == False:
                                    log.info("Discarding application as requested by user")
                                    submitted = False
                                    break

                            if "application was sent" in self.browser.page_source:
                                log.info("Application Submitted")
                                submitted = True
                                break
                            elif is_present(self.locator["easy_apply_button"]):
                                log.info("Skipping application")
                                submitted = False
                                break
                        continue
                        #add explicit wait
                    
                    else:
                        log.info("Application not submitted")
                        time.sleep(2)
                        break
                    # self.process_questions()

                elif len(self.get_elements("next")) > 0:
                    elements = self.get_elements("next")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()

                elif len(self.get_elements("review")) > 0:
                    elements = self.get_elements("review")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()

                elif len(self.get_elements("follow")) > 0:
                    elements = self.get_elements("follow")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()

        except Exception as e:
            log.error(e)
            log.error("cannot apply to this job")
            pass
            #raise (e)
        
        finally:
            # Always try to close the modal after attempting to apply
            self.close_easy_apply_modal()

        return submitted

    def save_unanswered_question(self, question):
        """Save unanswered question for later review"""
        # Only save each unique question once
        if question in self.unanswered_questions:
            return

        self.unanswered_questions.add(question)

        try:
            with open(self.unanswered_questions_file, 'a', encoding='utf-8') as f:
                # Extract potential keywords from the question
                keywords = ' '.join(question.lower().split()[:5])  # First 5 words
                f.write(f"- keywords: [\"TODO\"]  # Suggested: {keywords}...\n")
                f.write(f"  answer: \"TODO\"\n")
                f.write(f"  # Question: {question}\n\n")
            log.info(f"Saved unanswered question to {self.unanswered_questions_file}")
        except Exception as e:
            log.error(f"Error saving unanswered question: {e}")

    def ask_user_for_answer(self, question):
        """
        Interactive mode: Ask user to manually provide an answer for unknown question.
        Returns the user's answer or None if they want to skip.
        """
        print("\n" + "="*80)
        print("⚠️  MANUAL INPUT REQUIRED")
        print("="*80)
        print(f"\nQUESTION: {question}\n")
        print("Options:")
        print("  1. Enter your answer (press Enter to submit)")
        print("  2. Type 'skip' to skip this question")
        print("  3. Type 'discard' to discard this entire application")
        print("-"*80)

        user_input = input("Your answer: ").strip()

        if user_input.lower() == 'skip':
            log.info(f"User chose to skip question: '{question}'")
            return None
        elif user_input.lower() == 'discard':
            log.info(f"User chose to discard application due to question: '{question}'")
            return 'DISCARD_APPLICATION'
        elif user_input:
            log.info(f"User provided answer: '{user_input}' for question: '{question}'")

            # Ask if user wants to save this answer for future use
            save_prompt = input("\nSave this answer for future applications? (y/n): ").strip().lower()
            if save_prompt == 'y':
                # Extract keywords from question
                keywords_input = input("Enter keywords to match this question (comma-separated, or press Enter to auto-generate): ").strip()

                if keywords_input:
                    keywords = [k.strip() for k in keywords_input.split(',')]
                else:
                    # Auto-generate keywords from question
                    keywords = [question.lower().split()[:3]]  # First 3 words
                    keywords = [' '.join(keywords[0])]

                # Append to questions.yaml
                try:
                    with open("questions.yaml", 'a', encoding='utf-8') as f:
                        f.write(f"\n# Auto-added from interactive mode\n")
                        f.write(f"- keywords: {keywords}\n")
                        f.write(f"  answer: \"{user_input}\"\n")
                    log.info(f"Saved answer to questions.yaml with keywords: {keywords}")
                    print(f"✓ Answer saved to questions.yaml!")
                except Exception as e:
                    log.error(f"Error saving to questions.yaml: {e}")
                    print(f"✗ Failed to save: {e}")

            return user_input
        else:
            log.info(f"User provided empty answer, skipping question: '{question}'")
            return None

    def is_field_required(self, section):
        """
        Detect if a form field is required or optional.
        Returns: True if required, False if optional
        """
        try:
            # Strategy 1: Check for asterisk (*) or "required" text in the section
            section_html = section.get_attribute('innerHTML')
            if '*' in section.text or 'required' in section.text.lower():
                return True

            # Strategy 2: Check for aria-required attribute
            inputs = section.find_elements(By.CSS_SELECTOR, 'input, textarea, select')
            for input_elem in inputs:
                aria_required = input_elem.get_attribute('aria-required')
                if aria_required == 'true':
                    return True

                # Check for 'required' attribute
                if input_elem.get_attribute('required'):
                    return True

            # Strategy 3: Check for label with required indicator
            labels = section.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                if '*' in label.text or 'required' in label.text.lower():
                    return True

            # If none of the above, assume it's optional
            return False

        except Exception as e:
            log.debug(f"Error checking if field is required: {e}")
            # If we can't determine, assume it's required to be safe
            return True

    def process_questions(self):
        time.sleep(0.3)  # Brief wait for form sections to load
        form_sections = self.get_elements("fields")
        for section in form_sections:
            question = section.text
            answer = self.ans_question(question)

            # Check if user chose to discard application
            if answer == 'DISCARD_APPLICATION':
                log.warning(f"User chose to discard application. Stopping question processing.")
                return False  # Signal that application should be discarded

            if not answer:
                # Check if field is required
                is_required = self.is_field_required(section)
                if is_required:
                    log.warning(f"No answer found for REQUIRED question: '{question}'. Skipping - question logged for review.")
                else:
                    log.info(f"No answer found for optional question: '{question}'. Skipping as it's not required.")
                continue  # Don't block, just skip this question

            log.info(f"Answering question '{question}' with '{answer}'")

            try:
                # Type 1: Dropdowns
                dropdown_trigger = section.find_elements(By.CSS_SELECTOR, "button[aria-haspopup='listbox']")
                if dropdown_trigger:
                    dropdown_trigger[0].click()
                    time.sleep(0.3)  # Brief wait for dropdown to open
                    
                    option_xpath = f"//li[contains(@class, 'artdeco-dropdown__item')][contains(normalize-space(), '{answer}')]"
                    option = self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                    option.click()
                    continue

                # Type 2: Radio Buttons
                radio_buttons = section.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radio_buttons:
                    for radio in radio_buttons:
                        label = radio.find_element(By.XPATH, "./following-sibling::label")
                        if answer.lower() in label.text.lower():
                            radio.click()
                            break
                    continue

                # Type 3: Text Inputs
                text_inputs = section.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if text_inputs:
                    text_inputs[0].clear()
                    text_inputs[0].send_keys(answer)
                    continue
                
                # Type 4: Text Areas
                text_areas = section.find_elements(By.TAG_NAME, 'textarea')
                if text_areas:
                    text_areas[0].clear()
                    text_areas[0].send_keys(answer)
                    continue

            except Exception as e:
                log.error(f"Error answering question '{question}': {e}")


    def ans_question(self, question):
        question_lower = question.lower()

        # Strategy 1: Exact keyword match from questions.yaml
        if self.user_answers:
            for qa_pair in self.user_answers:
                if 'keywords' not in qa_pair or 'answer' not in qa_pair:
                    continue

                # Use any() to match if any keyword is in the question
                if any(keyword.lower() in question_lower for keyword in qa_pair['keywords']):
                    answer = qa_pair['answer']
                    log.info(f"[Exact match] Found keywords '{qa_pair['keywords']}' for question '{question}'. Answering with: '{answer}'")
                    self.answers[question] = answer
                    return answer

        # Strategy 2: Fuzzy keyword match (handle typos/variations)
        if self.user_answers:
            for qa_pair in self.user_answers:
                if 'keywords' not in qa_pair or 'answer' not in qa_pair:
                    continue

                for keyword in qa_pair['keywords']:
                    # Use fuzzy matching with 75% similarity threshold
                    similarity = SequenceMatcher(None, keyword.lower(), question_lower).ratio()
                    if similarity > 0.75:
                        answer = qa_pair['answer']
                        log.info(f"[Fuzzy match {similarity:.2%}] Matched keyword '{keyword}' for question '{question}'. Answering with: '{answer}'")
                        self.answers[question] = answer
                        return answer

        # Strategy 3: Question type detection with smart defaults

        # Years of experience questions (check this first before general yes/no)
        experience_patterns = ["how many years", "years of experience", "years' experience", "years experience"]
        if any(pattern in question_lower for pattern in experience_patterns):
            log.info(f"[Smart default] Detected experience question: '{question}'. Answering: '{self.years_of_experience}'")
            return str(self.years_of_experience)

        # Salary/compensation questions
        if any(word in question_lower for word in ["salary", "compensation", "pay expectation", "expected pay"]):
            log.info(f"[Smart default] Detected salary question: '{question}'. Using config salary: '{self.salary}'")
            return self.salary

        # Location questions
        if any(phrase in question_lower for phrase in ["location", "where are you located", "based in", "city", "state"]):
            if self.locations and len(self.locations) > 0:
                location = self.locations[0]
                log.info(f"[Smart default] Detected location question: '{question}'. Answering: '{location}'")
                return location

        # Availability/start date questions
        if any(phrase in question_lower for phrase in ["when can you start", "availability", "earliest start date", "notice period", "start date"]):
            log.info(f"[Smart default] Detected availability question: '{question}'. Answering with standard response")
            return "I am available to start two weeks after receiving an offer"

        # Notice period
        if "notice period" in question_lower or "how much notice" in question_lower:
            log.info(f"[Smart default] Detected notice period question: '{question}'. Answering: '2 weeks'")
            return "2 weeks"

        # Clearance questions
        if any(phrase in question_lower for phrase in ["security clearance", "clearance level", "government clearance"]):
            log.info(f"[Smart default] Detected clearance question: '{question}'. Answering: 'No'")
            return "No"

        # Drug test / background check
        if any(phrase in question_lower for phrase in ["drug test", "background check", "criminal background"]):
            log.info(f"[Smart default] Detected screening question: '{question}'. Answering: 'Yes'")
            return "Yes"

        # Commute questions
        if "commute" in question_lower:
            log.info(f"[Smart default] Detected commute question: '{question}'. Answering: 'Yes'")
            return "Yes"

        # References questions
        if "reference" in question_lower and ("provide" in question_lower or "have" in question_lower):
            log.info(f"[Smart default] Detected reference question: '{question}'. Answering: 'Yes'")
            return "Yes"

        # Management/team size questions
        if any(phrase in question_lower for phrase in ["team size", "how many people", "manage", "direct reports"]):
            log.info(f"[Smart default] Detected team/management question: '{question}'. Answering: '5'")
            return "5"

        # LinkedIn profile
        if "linkedin" in question_lower and ("profile" in question_lower or "url" in question_lower):
            log.info(f"[Smart default] Detected LinkedIn profile question: '{question}'. Answering: 'https://www.linkedin.com'")
            return "https://www.linkedin.com"

        # Website/portfolio
        if any(word in question_lower for word in ["website", "portfolio", "github"]) and ("url" in question_lower or "link" in question_lower):
            log.info(f"[Smart default] Detected portfolio/website question: '{question}'. Leaving blank (optional)")
            return ""

        # Cover letter / summary questions (leave blank if not in config)
        if any(phrase in question_lower for phrase in ["cover letter", "why do you want", "why are you interested", "tell us about yourself"]):
            log.info(f"[Smart default] Detected essay/cover letter question: '{question}'. Leaving blank (optional)")
            return ""

        # Education level
        if any(phrase in question_lower for phrase in ["education level", "highest degree", "level of education"]):
            log.info(f"[Smart default] Detected education question: '{question}'. Answering: 'Bachelor's Degree'")
            return "Bachelor's Degree"

        # GPA questions
        if "gpa" in question_lower:
            log.info(f"[Smart default] Detected GPA question: '{question}'. Answering: '3.5'")
            return "3.5"

        # Employment status
        if any(phrase in question_lower for phrase in ["currently employed", "employment status"]):
            log.info(f"[Smart default] Detected employment status question: '{question}'. Answering: 'Yes'")
            return "Yes"

        # Yes/No questions (this is a catch-all, so put it last)
        yes_no_patterns = ["are you", "do you", "have you", "will you", "can you", "did you", "would you"]
        if any(pattern in question_lower for pattern in yes_no_patterns):
            # Check for negative patterns that should be answered "No"
            negative_patterns = [
                "not authorized", "don't have", "haven't", "cannot", "can't", "won't",
                "require sponsorship", "need sponsorship", "visa sponsorship",
                "criminal", "convicted", "felony",
                "disability", "disabled",
                "non-compete", "non compete"
            ]
            if any(neg in question_lower for neg in negative_patterns):
                log.info(f"[Smart default] Detected negative yes/no question: '{question}'. Answering: 'No'")
                return "No"
            else:
                log.info(f"[Smart default] Detected yes/no question: '{question}'. Answering: 'Yes'")
                return "Yes"

        # Strategy 4: Interactive mode or log unanswered question
        log.warning(f"[No match] Could not find answer for question: '{question}'")

        # If interactive mode is enabled, ask user for answer
        if self.interactive_mode:
            user_answer = self.ask_user_for_answer(question)
            if user_answer == 'DISCARD_APPLICATION':
                # Signal to discard the application
                return 'DISCARD_APPLICATION'
            elif user_answer:
                return user_answer
            # If user skipped or provided empty answer, fall through to save and return None

        # Save unanswered question for later review
        self.save_unanswered_question(question)
        log.info("Skipping this question - will be saved for manual review")
        return None

    def load_page(self, sleep=0.1):
        scroll_page = 0
        while scroll_page < 4000:
            self.browser.execute_script("window.scrollTo(0," + str(scroll_page) + " );")
            scroll_page += 500
            time.sleep(sleep)

        if sleep != 0.1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep)

        page = BeautifulSoup(self.browser.page_source, "lxml")
        return page

    def avoid_lock(self) -> None:
        x, _ = pyautogui.position()
        pyautogui.moveTo(x + 200, pyautogui.position().y, duration=1.0)
        pyautogui.moveTo(x, pyautogui.position().y, duration=0.5)
        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(0.5)
        pyautogui.press('esc')

    def next_jobs_page(self, position, location, jobs_per_page, experience_level=[]):
        # Construct the experience level part of the URL
        experience_level_str = ",".join(map(str, experience_level)) if experience_level else ""
        experience_level_param = f"&f_E={experience_level_str}" if experience_level_str else ""
        self.browser.get(
            # URL for jobs page
            "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=" +
            position + location + "&start=" + str(jobs_per_page) + experience_level_param)
        #self.avoid_lock()
        log.info(f"Loading jobs page (start={jobs_per_page})")
        self.load_page()
        # Increment page number for next call (LinkedIn shows 25 jobs per page)
        jobs_per_page += 25
        return (self.browser, jobs_per_page)

    # def finish_apply(self) -> None:
    #     self.browser.close()


if __name__ == '__main__':

    with open("config.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert parameters['username'] is not None
    assert parameters['password'] is not None
    assert parameters['phone_number'] is not None


    if 'uploads' in parameters.keys() and type(parameters['uploads']) == list:
        raise Exception("uploads read from the config file appear to be in list format" +
                        " while should be dict. Try removing '-' from line containing" +
                        " filename & path")

    log.info({k: parameters[k] for k in parameters.keys() if k not in ['username', 'password']})

    output_filename: list = [f for f in parameters.get('output_filename', ['output.csv']) if f is not None]
    output_filename: list = output_filename[0] if len(output_filename) > 0 else 'output.csv'
    blacklist = parameters.get('blacklist', [])
    blackListTitles = parameters.get('blackListTitles', [])

    uploads = {} if parameters.get('uploads', {}) is None else parameters.get('uploads', {})
    for key in uploads.keys():
        assert uploads[key] is not None

    locations: list = [l for l in parameters['locations'] if l is not None]
    positions: list = [p for p in parameters['positions'] if p is not None]

    bot = EasyApplyBot(parameters['username'],
                       parameters['password'],
                       parameters['phone_number'],
                       parameters['salary'],
                       parameters['rate'],
                       uploads=uploads,
                       filename=output_filename,
                       blacklist=blacklist,
                       blackListTitles=blackListTitles,
                       experience_level=parameters.get('experience_level', []),
                       years_of_experience=parameters.get('years_of_experience', 8),
                       interactive_mode=parameters.get('interactive_mode', False)
                       )
    bot.start_apply(positions, locations)


