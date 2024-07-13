from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def scrape_amazon_data():
    try:
        
        # Initialize ChromeDriver with the specified service
        driver = webdriver.Chrome()
        
        # URL of the initial page
        url_Main = "https://www.amazon.com/?&tag=googleglobalp-20&ref=pd_sl_7nnedyywlk_e&adgrpid=159651196451&hvpone=&hvptwo=&hvadid=675114638367&hvpos=&hvnetw=g&hvrand=11970775233668718219&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9199207&hvtargid=kwd-10573980&hydadcr=2246_13468515&gad_source=1;"

        driver.get(url_Main)
        time.sleep(10) 
        
        # Fetch and parse data from the initial page using requests and BeautifulSoup
        response = requests.get(url_Main)
        soup = BeautifulSoup(response.text, "lxml")
        #print(soup)
       
        search = driver.find_element(By.XPATH, '/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[2]/div[1]/input')
        time.sleep(2)
        search.send_keys('eye liner')
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        search_result = BeautifulSoup(response.text, "lxml")
        
        base_url = 'https://www.amazon.com/s'
        search_query = 'eye+liner'
        params = {
            'k': search_query,
            'crid': '2CQCNIT0L3N77',
            'qid': '1720565889',
            'sprefix': 'eye+liner',
            'ref': 'sr_pg_'
            }
        
        products_names = []
        products_URL = []
        products_ASIN = []
        products_Description = []
        products_Price = []
        products_Images_URL = []
        products_Ratings = []
        products_No_Reviews = []

        for page_num in range(1, 8):
            cp_url = f'{base_url}?k={search_query}&page={page_num}&crid={params["crid"]}&qid={params["qid"]}&sprefix={params["sprefix"]}&ref={params["ref"]}{page_num}'
            driver.get(cp_url)
            time.sleep(3)  
            p2p_data = BeautifulSoup(driver.page_source, 'lxml')
            
            products_rows = p2p_data.find_all("div", class_="a-row a-color-base")
            for row in products_rows:
               if len(products_names) >= 240:
                   break
               spans = row.find_all("span", class_="a-size-base a-color-base s-background-color-platinum a-padding-mini aok-nowrap aok-align-top aok-inline-block a-spacing-top-micro puis-medium-weight-text")
               name = spans[0].text.strip()
               products_names.append(name)

        
            products_a = p2p_data.find_all("a", class_ ="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
            for a in products_a:
                if len(products_URL) >= 240:
                    break
                URL= a.get('href')
                products_URL.append("https://www.amazon.com" + URL)
                
            
            products_div = p2p_data.find_all("div", {'data-asin': True})
            for div in products_div:
                if len(products_ASIN) >= 240:
                    break
                ASIN = div.get('data-asin')
                products_ASIN.append(ASIN)
            
            products = p2p_data.find_all("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-3")
            for i in products:
                if len(products_Description) >= 240:
                    break
                Description = i.text
                products_Description.append(Description)
        
            products = p2p_data.find_all("span", class_="a-offscreen")
            for i in products:
                if len(products_Price) >= 240:
                    break
                Price = i.text
                products_Price.append(Price)
        
            products = p2p_data.find_all("div", class_="a-section aok-relative s-image-square-aspect")
            for product in products:
                if len(products_Images_URL) >= 240:
                    break
                image_urls = []  
                images_elem = product.find_all("img", class_="s-image")
                for img in images_elem:
                    image_url = img.get('src')
                    image_urls.append(image_url)
                concatenated_urls = ','.join(image_urls)
                products_Images_URL.append(concatenated_urls)

        
            products = p2p_data.find_all("i", class_="a-icon a-icon-star-small a-star-small-4-5 aok-align-bottom")
            for i in products:
                if len(products_Ratings) >= 240:
                    break
                rating = i.text.strip()
                rating_value = re.search(r'\d+\.\d+', rating)
                products_Ratings.append(rating_value.group())
            
        
            products = p2p_data.find_all("span", class_="a-size-base s-underline-text")
            for i in products:
                if len(products_No_Reviews) >= 240:
                    break
                Reviews = i.text
                products_No_Reviews.append(Reviews)
        
        # Check lengths before creating the DataFrame
        lengths = [
            len(products_URL),
            len(products_names),
            len(products_ASIN),
            len(products_Description),
            len(products_Price),
            len(products_Images_URL),
            len(products_Ratings),
            len(products_No_Reviews)
        ]
        
        print("Lengths of the lists:", lengths)
        if all(length == 240 for length in lengths):
            df = pd.DataFrame({
                
                "Product Name": products_names,
                "Product URL": products_URL,
                "Product ASIN": products_ASIN,
                "Product Description": products_Description, 
                "Product Price": products_Price,
                "products Image URL": products_Images_URL,
                "Products Reviews": products_No_Reviews

                })
            df.to_excel("Product_Detail.xlsx")
        
        
            


        
        
    finally:
        driver.quit()
       
if __name__ == '__main__':
    scrape_amazon_data()
