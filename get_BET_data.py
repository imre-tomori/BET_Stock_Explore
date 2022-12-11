#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime, timedelta
from time import sleep
import os


# In[2]:


def close_pop_up():

    cookie_banner = driver.find_element_by_id("cookie-warn")
    cookie_button = cookie_banner.find_element_by_tag_name("button")
    ticker_banner = driver.find_element_by_id("ticker")
    ticker_button = ticker_banner.find_element_by_xpath("//div[@class='ticker-show-hide hover-wrap-parent icon-eye-minus']")

    cookie_button.click()
    ticker_button.click()


# In[3]:


def adatletoltes_section(idoszakos_bontas_value, start_date_formatted, end_date_formatted, adatforma_value, adattipus_value):
    
    # időszakos bontás
    
    idoszakos_bontas = driver.find_element_by_id("select2-instrumentResolutionInput-container")
    idoszakos_bontas.click()
    idoszakos_bontas_category = driver.find_element_by_xpath("//ul[@id='select2-instrumentResolutionInput-results']//li[contains(., '" + idoszakos_bontas_value + "')]")
    idoszakos_bontas_category.click()
    
    # Dátum
    
    naptol_napig_start = driver.find_element_by_id("instrumentStartingDate")
    naptol_napig_start.clear()
    naptol_napig_start.send_keys(start_date_formatted)

    naptol_napig_end = driver.find_element_by_id("instrumentEndingDate")
    naptol_napig_end.clear()
    naptol_napig_end.send_keys(end_date_formatted)

    # Adatforma

    adatforma = driver.find_element_by_id("select2-dataFormatInput-container")
    adatforma.click()
    adatforma_category = driver.find_element_by_xpath("//ul[@id='select2-dataFormatInput-results']//li[contains(., '" + adatforma_value + "')]")
    adatforma_category.click()

    # Adattípus

    adattipus = driver.find_element_by_id("select2-dataTypeInput-container")
    adattipus.click()
    adattipus_category = driver.find_element_by_xpath("//ul[@id='select2-dataTypeInput-results']//li[contains(., '" + adattipus_value + "')]")
    adattipus_category.click()


# In[19]:


def azonnali_piac_section(azonnali_piac_value, first):
    
    # Indicator check to only open up accordion once
    
    if first:

        # Open up "Azonnali Piac" accordion

        accordion_banner = driver.find_element_by_id("prompt")
        accordion_banner.click()
    
    # Click "Kategória" drop down

    azonnali_piac = driver.find_element_by_id("select2-promptCategoryInput-container")
    azonnali_piac.click()
    
    # Select the specific category

    azonnali_piac_category = driver.find_element_by_xpath("//ul[@id='select2-promptCategoryInput-results']//li[contains(.,'" + azonnali_piac_value + "')]")
    azonnali_piac_category.click()
    
    active_elem = driver.switch_to.active_element
    active_elem.send_keys(Keys.ESCAPE)
    
    azonnali_piac_button = driver.find_element_by_id("promptButton")
    azonnali_piac_button.click()


# In[67]:


def get_BET_data(start_date, end_date, azonnali_piac_categories):
    
    # Clear out download directory
    stock_data_path = os.getcwd() + '\\Stock Data'
    [os.remove(stock_data_path+'\\'+stock_file) for stock_file in os.listdir(stock_data_path)]
    
    # Set up firefox profile to auto download the files

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", stock_data_path)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8")
    profile.update_preferences()

    ## Initialize driver
    global driver
    driver = webdriver.Firefox(firefox_profile=profile)

    try:
        driver.get('https://www.bet.hu/oldalak/adatletoltes')
    except:
        print ("Invalid URL")
        
    first = True

    ## Call functions

    # Remove cookie and ticker banner to not obscure other tags.
    close_pop_up()

    # Fill out "Adatletöltés" dropdown section
    adatletoltes_section('Naptól napig', start_date, end_date, 'Vesszővel elválasztott (.csv)', 'Részletes (értékek, átlagok, forgalom)')

    # Fill out "Azonnali piac" section

    for azonnali_piac_category in azonnali_piac_categories:

        azonnali_piac_section(azonnali_piac_category, first)
        
        sleep(3)
        first = False
    
    driver.close()
    
    return str(len(os.listdir(stock_data_path)))+'/'+str(len(azonnali_piac_categories))+ ' files downloaded.'


# In[68]:


### Main

if __name__ == "__main__":
    
    ## Declare variables

    # Max date range is 6 years
    end_date = datetime.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=6*365)
    end_date_formatted, start_date_formatted = end_date.strftime("%Y.%m.%d."), start_date.strftime("%Y.%m.%d.")

    azonnali_piac_categories = ['Részvények Prémium', 'Részvények Standard', 'Részvények T', 'ETF', 'Investment Certifikát']
    # 'Turbo Certifikát és Warrant' - this one breaks the download for some reason
    
    # Download stock data
    
    message = get_BET_data(start_date_formatted, end_date_formatted, azonnali_piac_categories)
    print(message)

