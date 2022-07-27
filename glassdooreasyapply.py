import time, random, csv, pyautogui, pdb, traceback, sys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
from itertools import product


class GlassDoorEasyApply:
    def __init__(self, parameters, driver):
        self.browser = driver
        self.email = parameters['email']
        self.password = parameters['password']
        self.disable_lock = parameters['disableAntiLock']
        self.company_blacklist = parameters.get('companyBlacklist', []) or []
        self.title_blacklist = parameters.get('titleBlacklist', []) or []
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.base_search_url = self.get_base_search_url(parameters)
        self.seen_jobs = []
        self.file_name = "output"
        self.output_file_directory = parameters['outputFileDirectory']
        self.resume_dir = parameters['uploads']['resume']
        self.photo_dir = parameters['uploads']['photo']
        if 'coverLetter' in parameters['uploads']:
            self.cover_letter_dir = parameters['uploads']['coverLetter']
        else:
            self.cover_letter_dir = ''
        self.checkboxes = parameters.get('checkboxes', [])
        self.university_gpa = parameters['universityGpa']
        self.languages = parameters.get('languages', [])
        self.industry = parameters.get('industry', [])
        self.technology = parameters.get('technology', [])
        self.personal_info = parameters.get('personalInfo', [])
        self.eeo = parameters.get('eeo', [])
        self.technology_default = self.technology['default']
        self.industry_default = self.industry['default']


    def login(self):
        try:
            self.browser.get("https://www.glassdoor.com/index.htm")
            time.sleep(random.uniform(1, 5))
            self.browser.find_element_by_css_selector('#SiteNav > nav > div.d-none.d-md-block.LockedHomeHeaderStyles__bottomBorder > div > div > div > button').click()
            self.browser.find_element_by_id("modalUserEmail").send_keys(self.email)
            self.browser.find_element_by_id("modalUserPassword").send_keys(self.password)
            self.browser.find_element_by_css_selector("#LoginModal > div > div > div.modal_main.actionBarMt0 > div.fullContent > div.modal_content > div > div > form > div.d-flex.align-items-center.flex-column > button > span").click()
            time.sleep(random.uniform(1, 5))
        except TimeoutException:
            raise Exception("Could not login!")

    def security_check(self):
        current_url = self.browser.current_url
        page_source = self.browser.page_source

        if '/checkpoint/challenge/' in current_url or 'security check' in page_source:
            input("Please complete the security check and press enter in this console when it is done.")
            time.sleep(random.uniform(5.5, 10.5))

    def check_notif_modal(self):
        try:
            self.browser.find_element_by_class_name("modal_main")
            self.browser.find_element_by_class_name("modal_closeIcon").click()
        except:
            pass
        
    def get_base_with_location(self, location, position):
        self.browser.find_element_by_id("sc.keyword").send_keys(position)
        loc = self.browser.find_element_by_id("sc.location")
        loc.send_keys(Keys.CONTROL + 'a')
        time.sleep(2)
        loc.send_keys(Keys.DELETE)
        time.sleep(3)
        loc = self.browser.find_element_by_id("sc.location")
        loc.send_keys(location)
        time.sleep(1)
        loc.send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        loc.send_keys(Keys.RETURN)
        time.sleep(2)
        self.browser.find_element_by_xpath('//*[@id="Discover"]/div/div/div[1]/div[1]/div[3]/a/strong').click()
        self.check_notif_modal()
        current_url = self.browser.current_url
        base_url = current_url.split('.htm')[0]
        return base_url + ".htm"
        
    def start_applying(self):
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)

        page_sleep = 0
        minimum_time = 30*1
        minimum_page_time = time.time() + minimum_time

        for (position, location) in searches:

            print("Starting the search for " + position + " in " + location + ".")
            base_url = self.get_base_with_location(location, position)
            job_page_number = -1


            try:
                while True:
                    page_sleep += 1
                    job_page_number += 1
                    print("Going to job page " + str(job_page_number))
                    self.next_job_page(base_url, job_page_number)
                    time.sleep(random.uniform(1.5, 3.5))
                    print("Starting the application process for this page...")
                    self.apply_jobs(location)
                    print("Applying to jobs on this page has been completed!")

                    time_left = minimum_page_time - time.time()
                    if time_left > 0:
                        print("Sleeping for " + str(time_left) + " seconds.")
                        time.sleep(time_left)
                        minimum_page_time = time.time() + minimum_time
                    if page_sleep % 5 == 0:
                        sleep_time = random.randint(50, 100)
                        print("Sleeping for " + str(sleep_time/60) + " minutes.")
                        time.sleep(sleep_time)
                        page_sleep += 1
            except:
                traceback.print_exc()
                pass

            time_left = minimum_page_time - time.time()
            if time_left > 0:
                print("Sleeping for " + str(time_left) + " seconds.")
                time.sleep(time_left)
                minimum_page_time = time.time() + minimum_time
            if page_sleep % 5 == 0:
                sleep_time = random.randint(100, 300)
                print("Sleeping for " + str(sleep_time/60) + " minutes.")
                time.sleep(sleep_time)
                page_sleep += 1


    def apply_jobs(self, location):
        no_jobs_text = ""
        try:
            no_jobs_element = self.browser.find_element_by_class_name('scaffold-layout__list-detail')
            no_jobs_text = no_jobs_element.text
        except:
            pass
        if 'No matching jobs found' in no_jobs_text:
            raise Exception("No more jobs on this page")

        if 'unfortunately, things aren' in self.browser.page_source.lower():
            raise Exception("No more jobs on this page")
        try:
            job_results = self.browser.find_element_by_id("MainCol")
            self.scroll_slow(job_results)
            self.scroll_slow(job_results, step=250, reverse=True)
# //*[@id="MainCol"]/div[1]/ul/li[1]
# //*[@id="MainCol"]/div[1]/ul/li[2]
            # job_list = self.browser.find_elements_by_class_name('scaffold-layout__list-container')[0].find_elements_by_class_name('jobs-search-results__list')
            job_list = self.browser.find_elements_by_xpath('//*[@id="MainCol"]/div[1]/ul/li')
        except:
            raise Exception("No more jobs on this page")

        if len(job_list) == 0:
            raise Exception("No more jobs on this page")

        for job_tile in job_list:
            job_title, company, job_location, apply_method, link = "", "", "", "", ""

            try:
                job_title = job_tile.find_element_by_class_name('eigr9kq1').find_element_by_tag_name('span').text
                link = job_tile.find_element_by_class_name('job-search-key-1rd3saf').get_attribute('href').split('?')[0]
            except:
                pass
            try:
                company = job_tile.find_element_by_class_name('e1n63ojh0').find_element_by_tag_name('span').text
            except:
                pass
            try:
                job_location = job_tile.find_element_by_class_name('e1rrn5ka').text
            except:
                pass
            try:
                apply_method = job_tile.find_element_by_class_name('job-card-container__apply-method').text
            except:
                pass

            contains_blacklisted_keywords = False
            job_title_parsed = job_title.lower().split(' ')

            for word in self.title_blacklist:
                if word.lower() in job_title_parsed:
                    contains_blacklisted_keywords = True
                    break

            if company.lower() not in [word.lower() for word in self.company_blacklist] and \
               contains_blacklisted_keywords is False and link not in self.seen_jobs:
                try:
                    job_el = job_tile.find_element_by_class_name('eigr9kq1')
                    job_el.click()

                    time.sleep(random.uniform(3, 5))

                    try:
                        done_applying = self.apply_to_job()
                        if done_applying:
                            print("Done applying to the job!")
                        else:
                            print('Already applied to the job!')
                        # self.browser.close()
                        # self.browser.switch_to.window(self.browser.window_handles[0])

                    except:
                        temp = self.file_name
                        self.file_name = "failed"
                        print("Failed to apply to job! Please submit a bug report with this link: " + link)
                        print("Writing to the failed csv file...")
                        try:
                            self.write_to_file(company, job_title, link, job_location, location)
                        except:
                            pass
                        self.file_name = temp

                    try:
                        self.write_to_file(company, job_title, link, job_location, location)
                    except Exception:
                        print("Could not write the job to the file! No special characters in the job title/company is allowed!")
                        traceback.print_exc()
                except:
                    traceback.print_exc()
                    print("Could not apply to the job!")
                    pass
            else:
                print("Job contains blacklisted keyword or company name!")
            self.seen_jobs += link

    def apply_to_job(self):
        easy_apply_button = None

        try:
            easy_apply_button = self.browser.find_element_by_class_name('e1mdf2m0')
        except:
            return False

        # try:
        #     job_description_area = self.browser.find_element_by_class_name("JDCol")
        #     self.scroll_slow(job_description_area, end=1200)
        #     self.scroll_slow(job_description_area, end=1200, step=400, reverse=True)
        # except:
        #     pass

        print("Applying to the job....")
        easy_apply_button.click()

        button_text = ""
        submit_application_text = 'Apply'
        while submit_application_text not in button_text.lower():
            retries = 3
            while retries > 0:
                try:
                    self.fill_up()
                    next_button = self.browser.find_element_by_class_name("icl-Button")
                    button_text = next_button.text.lower()
                    if submit_application_text in button_text:
                        try:
                            self.unhallow()
                        except:
                            print("Failed to unfollow company!")
                    time.sleep(random.uniform(1.5, 2.5))
                    next_button.click()
                    time.sleep(random.uniform(3.0, 5.0))

                    if 'please enter a valid answer' in self.browser.page_source.lower() or 'file is required' in self.browser.page_source.lower():
                        retries -= 1
                        print("Retrying application, attempts left: " + str(retries))
                    else:
                        break
                except:
                    traceback.print_exc()
                    raise Exception("Failed to apply to job!")
            if retries == 0:
                traceback.print_exc()
                self.browser.find_element_by_class_name('artdeco-modal__dismiss').click()
                time.sleep(random.uniform(3, 5))
                self.browser.find_elements_by_class_name('artdeco-modal__confirm-dialog-btn')[1].click()
                time.sleep(random.uniform(3, 5))
                raise Exception("Failed to apply to job!")

        closed_notification = False
        time.sleep(random.uniform(3, 5))
        try:
            self.browser.find_element_by_class_name('artdeco-modal__dismiss').click()
            closed_notification = True
        except:
            pass
        try:
            self.browser.find_element_by_class_name('artdeco-toast-item__dismiss').click()
            closed_notification = True
        except:
            pass
        time.sleep(random.uniform(3, 5))

        if closed_notification is False:
            raise Exception("Could not close the applied confirmation window!")

        return True

    def home_address(self, element):
        try:
            groups = element.find_elements_by_class_name('ia-UserFields')
            if len(groups) > 0:
                for group in groups:
                    lb = group.find_element_by_tag_name('label').find_element_by_tag_name('span').text.lower()
                    input_field = group.find_element_by_tag_name('input')
                    if 'street' in lb:
                        self.enter_text(input_field, self.personal_info['Street address'])
                    elif 'city' in lb:
                        self.enter_text(input_field, self.personal_info['City'])
                        time.sleep(5)
                        input_field.send_keys(Keys.DOWN)
                        time.sleep(1)
                        input_field.send_keys(Keys.RETURN)
                    elif 'zip' in lb or 'postal' in lb:
                        self.enter_text(input_field, self.personal_info['Zip'])
                    elif 'state' in lb or 'province' in lb:
                        self.enter_text(input_field, self.personal_info['State'])
                    else:
                        pass
        except:
            pass

    def get_answer(self, question):
        if self.checkboxes[question]:
            return 'yes'
        else:
            return 'no'

    def additional_questions(self):
        #pdb.set_trace()
        frm_el = self.browser.find_elements_by_class_name('icl-TextInput-wrapper')
        if len(frm_el) > 0:
            for el in frm_el:
                # Radio check
                try:
                    radios = el.find_element_by_class_name('jobs-easy-apply-form-element').find_elements_by_class_name('fb-radio')

                    radio_text = el.text.lower()
                    radio_options = [text.text.lower() for text in radios]
                    answer = "yes"

                    if 'driver\'s licence' in radio_text or 'driver\'s license' in radio_text:
                        answer = self.get_answer('driversLicence')
                    elif 'gender' in radio_text or 'veteran' in radio_text or 'race' in radio_text or 'disability' in radio_text or 'latino' in radio_text:
                        answer = ""
                        for option in radio_options:
                            if 'prefer' in option.lower() or 'decline' in option.lower() or 'don\'t' in option.lower() or 'specified' in option.lower() or 'none' in option.lower():
                                answer = option

                        if answer == "":
                            answer = radio_options[len(radio_options) - 1]
                    elif 'north korea' in radio_text:
                        answer = 'no'
                    elif 'sponsor' in radio_text:
                        answer = self.get_answer('requireVisa')
                    elif 'authorized' in radio_text or 'authorised' in radio_text or 'legally' in radio_text:
                        answer = self.get_answer('legallyAuthorized')
                    elif 'urgent' in radio_text:
                        answer = self.get_answer('urgentFill')
                    elif 'commuting' in radio_text:
                        answer = self.get_answer('commute')
                    elif 'background check' in radio_text:
                        answer = self.get_answer('backgroundCheck')
                    elif 'remote' in radio_text:
                        answer = self.get_answer('remote')
                    elif 'level of education' in radio_text:
                        for degree in self.checkboxes['degreeCompleted']:
                            if degree.lower() in radio_text:
                                answer = "yes"
                                break
                    elif 'level of education' in radio_text:
                        for degree in self.checkboxes['degreeCompleted']:
                            if degree.lower() in radio_text:
                                answer = "yes"
                                break
                    elif 'data retention' in radio_text:
                        answer = 'no'
                    elif 'drug' in radio_text:
                        answer = self.get_answer('drugTest')
                    else:
                        answer = radio_options[len(radio_options) - 1]

                    i = 0
                    to_select = None
                    for radio in radios:
                        if answer in radio.text.lower():
                            to_select = radios[i]
                        i += 1

                    if to_select is None:
                        to_select = radios[len(radios)-1]

                    self.radio_select(to_select, answer, len(radios) > 2)

                    if radios != []:
                        continue
                except:
                    pass
                # Questions check
                try:
                    question = el.find_element_by_class_name('jobs-easy-apply-form-element')
                    question_text = question.find_element_by_class_name('fb-form-element-label').text.lower()

                    txt_field_visible = False
                    try:
                        txt_field = question.find_element_by_class_name('fb-single-line-text__input')

                        txt_field_visible = True
                    except:
                        try:
                            txt_field = question.find_element_by_class_name('fb-textarea')

                            txt_field_visible = True
                        except:
                            pass

                    if txt_field_visible != True:
                        txt_field = question.find_element_by_class_name('multi-line-text__input')

                    text_field_type = txt_field.get_attribute('name').lower()
                    if 'numeric' in text_field_type:
                        text_field_type = 'numeric'
                    elif 'text' in text_field_type:
                        text_field_type = 'text'

                    to_enter = ''
                    if 'experience do you currently have' in question_text:
                        no_of_years = self.industry_default

                        for industry in self.industry:
                            if industry.lower() in question_text:
                                no_of_years = self.industry[industry]
                                break

                        to_enter = no_of_years
                    elif 'many years of work experience do you have using' in question_text:
                        no_of_years = self.technology_default

                        for technology in self.technology:
                            if technology.lower() in question_text:
                                no_of_years = self.technology[technology]

                        to_enter = no_of_years
                    elif 'grade point average' in question_text:
                        to_enter = self.university_gpa
                    elif 'first name' in question_text:
                        to_enter = self.personal_info['First Name']
                    elif 'last name' in question_text:
                        to_enter = self.personal_info['Last Name']
                    elif 'name' in question_text:
                        to_enter = self.personal_info['First Name'] + " " + self.personal_info['Last Name']
                    elif 'phone' in question_text:
                        to_enter = self.personal_info['Mobile Phone Number']
                    elif 'linkedin' in question_text:
                        to_enter = self.personal_info['Linkedin']
                    elif 'website' in question_text or 'github' in question_text or 'portfolio' in question_text:
                        to_enter = self.personal_info['Website']
                    elif 'summary' in question_text:
                        to_enter = self.personal_info['Summary']
                    elif 'headline' in question_text:
                        to_enter = self.personal_info['Headline']
                    elif 'education' in question_text:
                        to_enter = self.personal_info['University']
                    else:
                        if text_field_type == 'numeric':
                            to_enter = 0
                        else:
                            to_enter = " ‏‏‎ "

                    if text_field_type == 'numeric':
                        if not isinstance(to_enter, (int, float)):
                            to_enter = 0
                    elif to_enter == '':
                        to_enter = " ‏‏‎ "

                    self.enter_text(txt_field, to_enter)
                    continue
                except:
                    pass
                # Date Check
                try:
                    date_picker = el.find_element_by_class_name('artdeco-datepicker__input ')
                    date_picker.clear()
                    date_picker.send_keys(date.today().strftime("%m/%d/%y"))
                    time.sleep(3)
                    date_picker.send_keys(Keys.RETURN)
                    time.sleep(2)
                    continue
                except:
                    pass
                # Dropdown check
                try:
                    question = el.find_element_by_class_name('jobs-easy-apply-form-element')
                    question_text = question.find_element_by_class_name('fb-form-element-label').text.lower()

                    dropdown_field = question.find_element_by_class_name('fb-dropdown__select')

                    select = Select(dropdown_field)

                    options = [options.text for options in select.options]

                    if 'proficiency' in question_text:
                        proficiency = "Conversational"

                        for language in self.languages:
                            if language.lower() in question_text:
                                proficiency = self.languages[language]
                                break

                        self.select_dropdown(dropdown_field, proficiency)
                    elif 'country code' in question_text:
                        self.select_dropdown(dropdown_field, self.personal_info['Phone Country Code'])
                    elif 'north korea' in question_text:

                        choice = ""

                        for option in options:
                            if 'no' in option.lower():
                                choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    elif 'sponsor' in question_text:
                        answer = self.get_answer('requireVisa')

                        choice = ""

                        for option in options:
                            if answer == 'yes':
                                choice = option
                            else:
                                if 'no' in option.lower():
                                    choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    elif 'authorized' in question_text or 'authorised' in question_text:
                        answer = self.get_answer('legallyAuthorized')

                        choice = ""

                        for option in options:
                            if answer == 'yes':
                                # find some common words
                                choice = option
                            else:
                                if 'no' in option.lower():
                                    choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    elif 'citizenship' in question_text:
                        answer = self.get_answer('legallyAuthorized')

                        choice = ""

                        for option in options:
                            if answer == 'yes':
                                if 'no' in option.lower():
                                    choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    elif 'gender' in question_text or 'veteran' in question_text or 'race' in question_text or 'disability' in question_text or 'latino' in question_text:

                        choice = ""

                        for option in options:
                            if 'prefer' in option.lower() or 'decline' in option.lower() or 'don\'t' in option.lower() or 'specified' in option.lower() or 'none' in option.lower():
                                choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    else:
                        choice = ""

                        for option in options:
                            if 'yes' in option.lower():
                                choice = option

                        if choice == "":
                            choice = options[len(options) - 1]

                        self.select_dropdown(dropdown_field, choice)
                    continue
                except:
                    pass

                # Checkbox check for agreeing to terms and service
                try:
                    question = el.find_element_by_class_name('jobs-easy-apply-form-element')

                    clickable_checkbox = question.find_element_by_tag_name('label')

                    clickable_checkbox.click()
                except:
                    pass

    def unhallow(self):
        try:
            follow_checkbox = self.browser.find_element(By.XPATH, "//label[contains(.,\'to stay up to date with their page.\')]").click()
            follow_checkbox.click()
        except:
            pass

    def send_resume(self):
        try:
            file_upload_elements = (By.CSS_SELECTOR, "input[name='file']")
            if len(self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])) > 0:
                input_buttons = self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])
                for upload_button in input_buttons:
                    upload_type = upload_button.find_element(By.XPATH, "..").find_element(By.XPATH, "preceding-sibling::*")
                    if 'resume' in upload_type.text.lower():
                        upload_button.send_keys(self.resume_dir)
                    elif 'cover' in upload_type.text.lower():
                        if self.cover_letter_dir != '':
                            upload_button.send_keys(self.cover_letter_dir)
                        elif 'required' in upload_type.text.lower():
                            upload_button.send_keys(self.resume_dir)
                    elif 'photo' in upload_type.text.lower():
                        upload_button.send_keys(self.photo_dir)
        except:
            print("Failed to upload resume or cover letter!")
            pass


    def enter_text(self, element, text):
        element.clear()
        element.send_keys(text)

    def select_dropdown(self, element, text):
        select = Select(element)
        select.select_by_visible_text(text)

    # Radio Select
    def radio_select(self, element, label_text, clickLast=False):
        label = element.find_element_by_tag_name('label')
        if label_text in label.text.lower() or clickLast == True:
            label.click()
        else:
            pass

    # Contact info fill-up
    def contact_info(self):
        frm_el = self.browser.find_elements_by_class_name('jobs-easy-apply-form-section__grouping')
        if len(frm_el) > 0:
            for el in frm_el:
                text = el.text.lower()
                if 'email address' in text:
                    continue
                elif 'phone number' in text:
                    try:
                        country_code_picker = el.find_element_by_class_name('fb-dropdown__select')
                        self.select_dropdown(country_code_picker, self.personal_info['Phone Country Code'])
                    except:
                        print("Country code " + self.personal_info['Phone Country Code'] + " not found! Make sure it is exact.")
                    try:
                        phone_number_field = el.find_element_by_class_name('fb-single-line-text__input')
                        self.enter_text(phone_number_field, self.personal_info['Mobile Phone Number'])
                    except:
                        print("Could not input phone number.")

    def fill_up(self):
        try:
            time.sleep(2)
            # seems that this component may be hidden??? cannot find
            easy_apply_content = self.browser.find_element_by_xpath('//*[@id="ia-ApplyFormScreen"]/div[2]/form')
            b4 = easy_apply_content.find_element_by_class_name('ia-UserFields-fragment')
            pb4 = easy_apply_content.find_elements_by_class_name('ia-UserFields-fragment')
            if len(pb4) > 0:
                    try:
                        label = pb.find_element_by_tag_name('h3').text.lower()
                        try:
                            self.additional_questions()
                        except:
                            pass

                        try:
                            self.send_resume()
                        except:
                            pass

                        if 'Address' in label:
                            self.home_address(pb)
                        elif 'contact info' in label:
                            self.contact_info()
                    except:
                        pass
        except:
            pass
    
    def write_to_file(self, company, job_title, link, location, search_location):
        to_write = [company, job_title, link, location]
        file_path = self.output_file_directory + self.file_name + search_location + ".csv"

        with open(file_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(to_write)

    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.browser.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollable_element)
            time.sleep(random.uniform(1.0, 2.6))

    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')

    def get_base_search_url(self, parameters):
        remote_url = ""

        if parameters['remote']:
            remote_url = "?remoteWorkType=1"

        distance_url = "?radius=" + str(parameters['distance'])

        # job_types_url = "?jobType="
        # job_types = parameters.get('jobTypes', [])
        # for key in job_types:
        #     if job_types[key]:
        #         job_types_url += "%2C" + key.lower()

        date_url = ""
        if parameters['date']["Age"]:
            date_url = "&fromAge=" + str(parameters['date']['Age'])

        easy_apply_url = "&applicationType=1"

        extra_search_terms = [distance_url, remote_url]
        extra_search_terms_str = '&'.join(term for term in extra_search_terms if len(term) > 0) + easy_apply_url + date_url

        return extra_search_terms_str

    def next_job_page(self, base_url, job_page):
        self.browser.get(base_url + self.base_search_url)

        self.avoid_lock()

