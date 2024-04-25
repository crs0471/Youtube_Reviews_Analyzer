from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import sys
import logging
logging.getLogger('selenium').setLevel(logging.WARNING)

def print_process(i:int):
    sys.stdout.write(f"\r \033[94mProcess : {'='*i}{'-'*(10-i)}\033[0m")
    sys.stdout.flush()

def print_process_no_count(i:int):
    sys.stdout.write(f"\r \033[94mFetching Reviews : {'.'*i}\033[0m")
    sys.stdout.flush()


PRODUCTION = 1

def scroll_and_get_rev(driver, scroll_height=0):
    if not PRODUCTION :print(">> scrolling ..")
    break_counter = 5
    review_containers = []

    while not review_containers:
        scroll_height += 200
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(1)
        review_containers = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
        if review_containers:
            if not PRODUCTION : print(f">> {len(review_containers)} reviews found")
            driver.execute_script("arguments[0].scrollIntoView();", review_containers[-1])
        if not review_containers :
            break_counter -= 1
            time.sleep(2)
            if not PRODUCTION :print(f">> Reviews not found. (Try remaining {break_counter})")
        if break_counter < 0 : break
    return review_containers, scroll_height

def scroll_to_bottom(driver):
    break_counter = 10
    iter = 1 
    print('\n')
    while True:
        print_process_no_count(iter)
        iter += 1       
        if iter > 10 : iter = 1
        ph = driver.execute_script("return document.documentElement.scrollHeight;")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight)")
        time.sleep(0.5)
        ch = driver.execute_script("return document.documentElement.scrollHeight;")
        if ch == ph:
            break_counter -= 1
            if break_counter < 0 : break
        else: break_counter = 3
    print('\n')
    

def scrape_reviews(video_link):
    if PRODUCTION : print(">> Scraping reviews, till then you can scroll your instagram reel section 😁 ..")
    if PRODUCTION : print_process(1)

    
    chrome_options = Options()
    if PRODUCTION :chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(video_link)

    if PRODUCTION : print_process(4)
    driver.implicitly_wait(10)
    desc = driver.find_element(By.ID, "description")
    # scroll to desc 
    driver.execute_script("arguments[0].scrollIntoView();", desc)
    time.sleep(2)
    review_containers, scroll_height = scroll_and_get_rev(driver)
    scroll_to_bottom(driver)

    review_texts = set([])
    if PRODUCTION : print_process(6)
    review_containers = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")

    def rev_collector(review_containers):
        for review in review_containers:
            text = review.find_element(By.CSS_SELECTOR, 'yt-attributed-string#content-text')
            review_texts.add(text.text)
        return review_texts
    if PRODUCTION : print_process(8)    

    review_texts = rev_collector(review_containers)
    if PRODUCTION : print_process(10)
    if PRODUCTION : print("\n>> hurrye, We did it 🥳🥳.")

    if not PRODUCTION :print('Numbers of Review: ', len(review_texts))
    return review_texts


def get_sentiment(review):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(review)
    return ss

def create_sentiment_file(reviews):
    if PRODUCTION : print(">> Creating data file, It will be complete until you complete a cup of tea..")

    df = pd.DataFrame(columns=['review_text', 'negativity', 'positivity', 'neutrality'])

    for review in reviews:
        ss = get_sentiment(review)
        df.loc[len(df)] = {'review_text': review, 'negativity': ss['neg'], 'positivity': ss['pos'], 'neutrality': ss['neu']}

    df.to_csv('sentiment.csv', index=False)
    get_sentiment_overview(df)
    return df

def get_sentiment_overview(df):
    print(f"""
    Number of reviews: {len(df)}
    Average positivity: {df['positivity'].mean()}
    Average negativity: {df['negativity'].mean()}
    Average neutrality: {df['neutrality'].mean()}
    """)

    return df.describe()

def run():
    choice  = input('''Enter 1 to scrape reviews from youtube and 2 for overview sentiment file :''')
    if choice == "1":
        video_link = input("Enter youtube link: ")
        reviews = scrape_reviews(video_link)
        create_sentiment_file(reviews)
    else:
        df = pd.read_csv('sentiment.csv')
        get_sentiment_overview(df)

if __name__ == "__main__":
    run()
    input('>>> Press any key to exit ...')
    

