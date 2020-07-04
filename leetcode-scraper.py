'''
Author: Abhishek Goyal

LeetCode Scraper is a python program that logins into your LeetCode account, and copies your code for your solved 
problems into its corresponding file.

For example, your solution to the problem <name> will be stored in the file <name>.cpp
'''

TIME_DELAY = 10
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

chrome_options = Options()
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(TIME_DELAY)

def go_to_algorithms():
    make_directory("./leet_code_solutions")
    driver.get("https://leetcode.com/problemset/algorithms/")
    solved_dropdown = driver.find_element_by_xpath(
        '//*[@id="question-app"]/div/div[2]/div[2]/div'
        '/div[2]/div[4]'
    )
    solved_dropdown.click()
    all_dropdown = driver.find_element_by_xpath(
        '//*[@id="question-app"]/div/div[2]/div[2]/div/div[2]'
        '/div[4]/div/div/div/div[2]'
    )
    all_dropdown.click()

    # Opens every problem and then copies their data into a file
    table = driver.find_element_by_class_name('reactable-data')
    problems = {}
    for row in table.find_elements_by_tag_name("tr"):
        title = row.find_element_by_tag_name("a").text
        href = row.find_element_by_tag_name("a").get_attribute("href")
        problems[title] = href
    for title in problems:
        code = scrape_code(problems[title])
        create_file(title, code)

def filter_submissions(submissions):
    def better_of(s1, s2):
        if s2[3] == 'N/A':
            return s1
        elif s1[3] == 'N/A':
            return s2
        else:
            t1 = int(s1[3].split()[0])
            t2 = int(s2[3].split()[0])
            return s2 if t1 > t2 else s1
    submissions_to_save = dict()
    for submission in submissions:
        problem_name = submission[1]
        if submissions_to_save.get(problem_name) is None:
            submissions_to_save[problem_name] = submission
        else:
            submissions_to_save[problem_name] = better_of(submissions_to_save[problem_name], submission)
    return submissions_to_save

def get_code(submission):
    driver.get(submission[-1])
    code_box = driver.find_element_by_xpath('//*[@id="ace"]/div/div[3]/div').click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
    code = pyperclip.paste()
    problem_link = '// ' + driver.find_element_by_xpath('//*[@id="submission-app"]/div/div[1]/h4/a').get_attribute('href') + '\n'
    info = '// ' + submission[2] + '    ' + submission[3] + '\n\n'
    return problem_link + info + code

def save_codes():
    path = './LeetCode/'
    os.makedirs(path, exist_ok=True)
    for problem_name in submissions_to_save:
        code = get_code(submissions_to_save[problem_name])
        code_lang = submissions_to_save[problem_name][-2]
        file_path = path + problem_name.replace(' ', '_') + '.' + code_lang
        with open(file_path, 'w') as f:
            f.write(code)

def sign_into_leetcode(username, password):
    driver.get("https://leetcode.com/accounts/login/")
    driver.find_element_by_xpath('// *[ @ id = "id_login"]').send_keys(username)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(password)
    driver.find_element_by_xpath('// *[ @ id = "id_password"]').send_keys(Keys.ENTER)

def get_submissions():
    driver.get('https://leetcode.com/submissions/')
    submissions = []
    while True:
        table = driver.find_element_by_xpath('//*[@id="submission-list-app"]/div/table')
        head = table.find_element_by_tag_name('thead')
        body = table.find_element_by_tag_name('tbody')
        for row in body.find_elements_by_tag_name('tr'):
            row = row.find_elements_by_tag_name('td')
            submissions.append([col.text for col in row] + [row[2].find_element_by_tag_name('a').get_attribute('href')])
        try:
            next_button = driver.find_element_by_xpath('//*[@id="submission-list-app"]/div/nav/ul/li[2]/a')
        except NoSuchElementException:
            break
        next_button.click()
    return submissions

if __name__ == "__main__":
    sign_into_leetcode(username='', password='')
    input('proceed?')
    submissions = get_submissions()
    with open('all_submissions.json', 'w') as f:
        json.dump(submissions, file=f)
    submissions_to_save = filter_submissions(submissions)
    with open('submissions_to_save.json', 'w') as f:
        json.dump(submissions_to_save, file=f)
    save_codes(submissions_to_save)
    # go_to_algorithms()
    driver.close()