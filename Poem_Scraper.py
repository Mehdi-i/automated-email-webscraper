
import mysql.connector
from bs4 import BeautifulSoup
import requests
import re
from dotenv import load_dotenv
import os

WebURL = "https://www.lovepoemsandquotes.com/LovePoem01.html"

def connect_Database():
    load_dotenv()
    database = mysql.connector.connect(
        host = os.getenv("host"),
        user = os.getenv("user"),
        password = os.getenv("password"),
        database = os.getenv("database")
    )
    print("Connected to the Database")

    cursor = database.cursor()
    sqlcommand = "SHOW TABLES LIKE 'poems'"
    cursor.execute(sqlcommand)
    result = cursor.fetchone()
    if result:
        print("poem table exists")
    else:
        sqlcommand = """Create table poems (
	                    Poem_id int AUTO_INCREMENT PRIMARY KEY,
                        Poem_name varchar(255),
                        Poem_content text NOT NULL,
                        author varchar(255),
                        date_sent date,
                        is_sent bool Default False
                    )"""
        cursor.execute(sqlcommand)

    return database, cursor


def webscrape(link):
    request = requests.get(link)
    soup = BeautifulSoup(request.content, 'html5lib')
    tables = soup.find_all('td', attrs={'class': 'stxt'})

    for table in tables:
        if table.find("strong") and not table.find("a"):
            table = table.text.split("\n")

            for t in range(len(table)-1, -1, -1):
                if table[t].strip() == '':
                    del table[t]

            title = table[0] + ":"
            del table[0] 
            author = table[-1]
            table.pop()
            cleaned_content = "\n".join(table)

            return title, cleaned_content, author
        
    return None, None, None


def LinkManipulate(url):
    separate = url.split('/')[-1]
    link_index = re.search(r'\d+', separate)
    if link_index:
        start = link_index.start()
        end = link_index.end()
    digit = str(int(link_index.group(0)) + 1).zfill(2)
    new_separate = separate[:start] + digit + separate[end:]
        
    separate = url.split('/')
    separate[-1] = new_separate
    separate = '/'.join(separate)
    url = separate
        
    return url


def SQLRecorder():
    database, cursor = connect_Database()
    iterations = 365
    current_url = WebURL
    
    for iter in range(iterations):
        try:
            title, poem_content, author = webscrape(current_url)
            insert_query = """INSERT INTO poems (Poem_name, Poem_content, author)
            VALUES (%s, %s, %s)"""
            cursor.execute(insert_query, (title, poem_content, author))
            database.commit()
            print(f"{title.strip()} inserted successfully!")

            current_url = LinkManipulate(current_url)

        except Exception as e:
            request = requests.get(current_url)
            soup = BeautifulSoup(request.content, 'html5lib')
            tables = soup.find_all('td', attrs={'class': 'stxt'})
            if len(tables) >= 2:
                current_url = LinkManipulate(current_url)
                continue
            else:
                current_url = LinkManipulate(current_url)
                continue
    database.close()

SQLRecorder()