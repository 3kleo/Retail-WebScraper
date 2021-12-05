# gets links from csv within directory with prefered sizes for items and trigger price for alerts

# imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
from time import sleep
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

selector = '_3teszy'  # change this to the respective selector of your prefered website
delay = 20  # seconds
log = ""
shopping_list = pd.read_csv('shopping_list.csv', sep=';')


def get_html_from_page():
    """
    Opens a webpage, waits for all elements to load and then iterates through
    every single color/model of the item, appending each HTML code to the sources_list list.

    Returns
    -------
    sources_list list containing the HTML code for all models of the product in the url
    """

    global log
    sources_list = []
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    browser.fullscreen_window()

    try:
        # wait for data to be loaded
        WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, selector))
        )
        # list of colors of item
        btns = browser.find_elements(By.CLASS_NAME, 'box-color')

        # iterate through all colors and get html
        for btn in btns:
            # WebDriverWait(browser, delay).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, 'box-color')))

            sleep(3)
            btn.click()
            sources_list.append(browser.page_source)

    except TimeoutException:
        log = log + f'{datetime.today().strftime("%d/%m/%Y %H:%M:%S")} - Link not working for {url}\n'
        print("Loading took too much time!")

    finally:
        sleep(3)
        browser.quit()

    return sources_list


def get_elements_from_html():
    """
    Scrapes the price, item name, color/model and checks if prefered size is available. Register current price,
    and size check to excel file "itens" in the same directory.

    Compares current price with lower price registered. Alerts in case of new low price.
    """

    global log
    prices_log = pd.read_excel('itens.xlsx')

    for source in sources:

        # scrape properties from html
        soup = BeautifulSoup(source, features="lxml")  # turns into BeatifulSoup object
        span_tags = soup.find('span', {'class': '_3teszy'})
        curr_price = float(span_tags.text.strip('R$ ').replace(',', '.'))
        item_name = soup.find('h1', {'class': '_gjoabl'}).text
        sizes = [x.text for x in soup.find_all('div', {'class': '_1uax8x0'})]
        my_size = sum([x in sizes for x in target_sizes]) > 0
        curr_color = soup.find('h3', {'class': '_3lyjer color-selected-label'}).text[5:]
        curr_datetime = datetime.now()
        mail_check = False

        # check if item and color is already in the file
        if len(prices_log.query('name == @item_name and color == @curr_color').index) == 0:

            price_dict = {'name': item_name, 'my_size': my_size, 'color': curr_color,
                          'last_price': curr_price, 'date_last_price': curr_datetime,
                          'high_price': curr_price, 'date_high_price': curr_datetime,
                          'low_price': curr_price, 'date_low_price': curr_datetime,
                          }
            prices_log = prices_log.append(price_dict, ignore_index=True)
            log = log + f'{datetime.today().strftime("%d/%m/%Y %H:%M:%S")} - Added item {item_name} - {curr_color}\n'
            continue

        # fill values
        current_item = (prices_log['name'] == item_name) & (prices_log['color'] == curr_color)
        position = prices_log[current_item].index
        prices_log.at[position[0], 'last_price'] = curr_price
        prices_log.at[position[0], 'date_last_price'] = curr_datetime
        prices_log.at[position[0], 'my_size'] = my_size

        # checks for new low price
        if target_price >= curr_price:
            if not mail_check:
                try:
                    send_mail(url, item_name, curr_price, my_size, curr_color)
                    mail_check = True

                except Exception as erro:
                    print(f'Error {erro.__class__}')

        if float(prices_log.loc[current_item, 'low_price']) > curr_price:

            prices_log.loc[current_item, 'low_price'] = curr_price
            prices_log.loc[current_item, 'date_low_price'] = curr_datetime

            log = log + f'{datetime.today().strftime("%d/%m/%Y %H:%M:%S")} - New low price on item {item_name} - {curr_color}\n'

            if not mail_check:
                try:
                    send_mail(url, item_name, curr_price, my_size, curr_color)
                    mail_check = True

                except Exception as erro:
                    print(f'Error {erro.__class__}')

            print('alert new low price')

        elif float(prices_log.loc[current_item, 'high_price']) < curr_price:

            prices_log.loc[current_item, 'high_price'] = curr_price
            prices_log.loc[current_item, 'date_high_price'] = curr_datetime

    prices_log.to_excel('itens.xlsx', index=False)


def send_mail(link, product, price, size, color):
    """
    Sends an email through gmail account alerting of a price found on item.
    """
    port = 465  # For SSL
    password = "password"  # generated app password

    sender_email = "sender@gmail.com"  # your email (gmail)
    receiver_email = "receiver@whatever.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Alert for {product} on Centauro"
    message["From"] = formataddr(('Your WebScraper', sender_email))
    message["To"] = receiver_email

    # send both HTML and plain text version of the same email
    text = f"""\
        Hi,
        I found the item {product} {color} for R$ {price}! Your size {"is" if size else "isn't"} available
        Click the link below for more information
        {link}
        """

    mail_html = f"""\
        <html>
          <body>
            <p>Hi,<br>
               I found the item {product} {color} for R$ {price}! Your size {"is" if size else "isn't"} available. <br> 
               Click the <a href="{link}">link</a> for more information.
            </p>
          </body>
        </html>
        """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(mail_html, "html")

    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


if __name__ == "__main__":

    for label, row in shopping_list.iterrows():
        url = row['link']
        target_sizes = row['size(s)'].split(',')
        target_price = row['buy_below']

        print(f'checking link {url}')
        try:
            sources = get_html_from_page()
        except Exception as erro:
            print(f'Error {erro.__class__}')
            continue
        try:
            get_elements_from_html()
        except Exception as erro:
            print(f'Error {erro.__class__}')
            continue

    # writes log to file
    with open("Log.txt", "a") as text_file:
        text_file.write(log)
