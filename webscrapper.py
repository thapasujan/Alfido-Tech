import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import os

def get_soup(url):
    #fetch & parses a url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.179 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'lxml')
    else:
        print(f"Error fetching page:{response.status_code}")
        return None
    
def scrape_data(url, data_type, num_pages=1):
    #Scrapes the specified type of data from a website
    data = []

    for page in range(1, num_pages+1):
        print(f"Scraping page {page}...")
        soup = get_soup(url.format(page=page))
        if soup:
            if data_type == "headlines":
                headlines = soup.find_all('h2')
                data.extend([headline.text.strip() for headline in headlines])
            
            elif data_type == "product":
                products = soup.find_all('div', class_ = 'product-item')
                for product in products:
                    title = product.find('h2').text.strip()
                    price = product.find('span', class_='price').text.strip()
                    data.append({'title':title, 'price':price})

            elif data_type == "jobs":
                job_listings = soup.find_all('div', class_='job-listing')
                for job in job_listings:
                    title = job.find('h2').text.strip()
                    company = job.find('span', class_='company').text.strip()
                    data.append({'title':title, 'company':company})

            else:
                print("Skipping page due to an error.")
        return data
    
def save_to_csv(data, file_name = "output.csv"):
    #saves the scraped data to csv file
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}.")

def save_to_database(data, db_name = "scraped_data.db", table_name="data"):
    #saves scraped data to an SQLite database
    conn = sqlite3.connect(db_name)
    df = pd.DataFrame(data)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"data saved to SQLite database {db_name}.")

def main():
    url = input("Enter the URL to scrape:")
    data_type = input("Enter the type of data to scrape (headlines, product, jobs):")
    num_pages = int(input("Enter the number of pages to scrape:"))
    output_format = input("Save to CSV or database(db)? :").lower()

    data = scrape_data(url, data_type, num_pages)

    if data:
        if output_format == 'csv':
            file_name = input("Enter the CSV file name (Eg: 'data.csv'):")
            save_to_csv(data, file_name)
            
        elif output_format == 'db':
            db_name = input("Enter the SQLite database name (Eg: 'data.db'):")
            table_name = input("Enter the table name:")
            save_to_database(data, db_name, table_name)

        else:
            print("Invalid output format selected.")
    else:
        print("No data scraped.")
if __name__ == "__main__":
    main()