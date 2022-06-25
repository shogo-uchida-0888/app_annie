"""
app annie web scraping
Author: Shogo
with little test
"""
import sys
sys.path.append(r"C:\Users\sh_uchida\Desktop\tech_centre\venv\Lib\site-packages\bs4")
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.keys import Keys


# config


options = Options()
options.add_argument('--headless')
# Headlessモードを有効にする
# 引数をTrueに設定するとブラウザを起動させず実行できます
# options.headless = False

# GoogleSpreadSheet connect
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(r'product-perry-c65da608500f.json', scope)
gc = gspread.authorize(credentials)

SPREADSHEET_KEY = '1oXW3drWqNFWaIYKSgIC83w6VF-NKndSBmPyx2BacZZA'
worksheet_main = gc.open_by_key(SPREADSHEET_KEY).worksheet('main')
worksheet_DB = gc.open_by_key(SPREADSHEET_KEY).worksheet('DB')



# Chromeを起動する　　
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome(executable_path=r'C:\Users\sh_uchida\Desktop\tech_centre\chromedriver_win32\chromedriver.exe')
driver.implicitly_wait(10)

# App Annieのログイン情報
url = "https://www.appannie.com/account/login"
userid = "johnny@septeniamerica.com"
password = "GoPerry7"

proxies_dic = {
    "http": "http://172.17.10.42:8080",
    "https": "http://172.17.10.42:8080",
}

response = driver.get(url)

# login, password
driver.find_element_by_xpath("//input[@placeholder='Email']").send_keys(userid)
driver.find_element_by_xpath("//input[@placeholder='Password']").send_keys(password)
driver.find_element_by_name("remember_me").click()
driver.find_element_by_tag_name('button').click()

sleep(25)


# default setting
def default():
    driver.find_element_by_xpath("//input[@placeholder='Start typing to search']").send_keys("荒野行動-AIR")
    driver.find_elements_by_css_selector(".Text-wvugs1-0.SmallApp__Name-sc-19bw7jx-1.gGQeIu")[0].click()
    # calender click
    driver.find_element_by_name("date-picker-v2").click()
    # week click
    driver.find_elements_by_css_selector(".Touchable__TouchableBase-vey7x-0.inmPVO.flexview__FlexView-sc-15q74yn-0"
                                         ".DatePickerShortcuts__Shortcut-sc-1t84r58-0.dZdcom.FlexView")[1].click()
    # Done click
    driver.find_element_by_css_selector(".Touchable__TouchableBase-vey7x-0.inmPVO"
                                       ".styles__ButtonBase-sc-1djd7ba-0.gulSoA.button-primary.is-medium").click()



def main():
    count = worksheet_main.cell(1, 1).value

    for i in range(int(count)):
        #for num in range(2):
        lastrow1, ID_list = get_lastrow()
        try:
            appname = choose_app(0, i)
        except:
            continue
        type = os_judge()
        appname, type, ID, title, check, campaign, media = get_title_ID(type, appname, i) # appname will be the same
        print("appname : " + appname)
        if ID in ID_list:
            print("found the same app in our DB")
            continue
        paste_title_ID(appname, type, ID, title, check, campaign, media, lastrow1, appname)
        get_numbers(lastrow1)
        get_categorys(lastrow1)

        judge = lookalike_judge()
        if not judge:
            print("no lookalike app")
            continue

        for m in range(10):
            print("-------------- in lookalike loop ------------------")
            lastrow1, ID_list = get_lastrow()
            sleep(5)
            lookalikeapplist = driver.find_elements_by_css_selector(".Text-wvugs1-0.jsWCXI")
            try:
                lookalikeapp = lookalikeapplist[m].text
            except:
                continue
            print("lookalike app is " + lookalikeapp + "number : " + str(m))
            sleep(5)
            driver.find_elements_by_css_selector(".Text-wvugs1-0.jsWCXI")[m].click()

            type = os_judge()
            lookalike, type, ID, title, check, campaign, media = get_title_ID(type, lookalikeapp, i)
            media = "N/A"
            if ID in ID_list:
                print("found the same app in our DB")
                continue
            print("original app name" + appname)
            paste_title_ID(lookalikeapp, type, ID, title, check, campaign, media, lastrow1, appname)
            get_numbers(lastrow1)
            get_categorys(lastrow1)
            driver.back()
            lastrow1 += 1



def lookalike_judge():
    elements_list = driver.find_elements_by_css_selector(".Typography__Title-scnz1m-0.gbScYT")
    texts_list = []
    for elem in elements_list:
        texts_list.append(elem.text)
    print(texts_list)
    lookalike_judge = "Users may also like" in texts_list
    return lookalike_judge




def get_lastrow():
    values1 = worksheet_DB.get_all_values()
    lastrow1 = len(values1) + 1
    print("last raw" + str(lastrow1))
    ID_list = worksheet_DB.col_values(4)
    return lastrow1, ID_list

def choose_app(num, i):
    print("os select number" + str(num))
    # get the title from gsheet
    appname = worksheet_main.cell(i + 3, 1).value
    # click on either first or second result
    #if num % 2 == 0:
    #    click_select = 0
    #else:
    #    click_select = 1
    click_select = 0

    driver.find_element_by_xpath("//input[@placeholder='Start typing to search']").send_keys(appname)
    sleep(3)
    driver.find_elements_by_css_selector(".Text-wvugs1-0.SmallApp__Name-sc-19bw7jx-1.gGQeIu")[click_select].click()
    sleep(3)
    return appname


def os_judge():
    # ios or google : type == "ios" or type == "google-play":
    try:
        # google
        AppIcon = driver.find_element_by_css_selector(".AppIcon__StoreImage-sc-1tw1nlk-0.bGNUmN")
    except:
        # Apple
        AppIcon = driver.find_element_by_css_selector(".AppIcon__StoreImage-sc-1tw1nlk-0.hmwJtD")
    finally:
        type = AppIcon.get_attribute("type")
        if type == "google-play":
            type = "android"

    return type



def get_title_ID(type, appname, i):

    title = driver.find_element_by_css_selector(".Typography__Title-scnz1m-0."
                                        "HeaderLayout__Name-sc-1pcxd10-1.jFinRy").text
    # get IDs
    ID = driver.find_element_by_css_selector(".Text-wvugs1-0.hdHUgB").text
    ID = ID[8:]

    # check app
    check = title in appname or appname in title or appname in ID or ID in appname

    # get campaign and media names
    campaign = worksheet_main.cell(i + 3, 2).value
    media = worksheet_main.cell(i + 3, 3).value

    return appname, type, ID, title, check, campaign, media

def paste_title_ID(lookalikeapp, type, ID, title, check, campaign, media , lastrow1, appname):
    # output for A, B, C, D, E, X, Y, Z columns
    worksheet_DB.update_cell(lastrow1, 1, lookalikeapp)
    worksheet_DB.update_cell(lastrow1, 3, type)
    worksheet_DB.update_cell(lastrow1, 4, ID)
    worksheet_DB.update_cell(lastrow1, 5, title)
    worksheet_DB.update_cell(lastrow1, 6, check)
    worksheet_DB.update_cell(lastrow1, 24, appname)
    worksheet_DB.update_cell(lastrow1, 25, campaign)
    worksheet_DB.update_cell(lastrow1, 26, media)


def get_numbers(lastrow1):

    # for G - R columns
    # loop period first, loop GEO later
    periods = [1, 4]
    geos = ["jp", "us", "ww"]
    column_count = 7 # starting from G column
    for period in periods:
        # calender click
        driver.find_element_by_name("date-picker-v2").click()
        # period selection
        driver.find_elements_by_css_selector(".Touchable__TouchableBase-vey7x-0.inmPVO"
                                             ".flexview__FlexView-sc-15q74yn-0."
                                             "DatePickerShortcuts__Shortcut-sc-1t84r58-0.dZdcom.FlexView")[period].click()


        # 「Done」click
        driver.find_element_by_css_selector(".Touchable__TouchableBase-vey7x-0.inmPVO"
                                            ".styles__ButtonBase-sc-1djd7ba-0.gulSoA.button-primary.is-medium").click()
        for geo in geos:
            driver.find_element_by_id("react-select-SingleCountryPicker--__common__--value-item").click()
            driver.find_element_by_css_selector(".Flag__StyledFlag-sc-161hlrc-0.fOybwW.flag-icon-" + geo).click()
            sleep(3)

            # get DL number
            download = driver.find_elements_by_css_selector(".Text-wvugs1-0.Summary__SectionBody-tv96kb-2"
                                                            ".gboEcw.Summary__MetricWrapper.summary-value")[0]
            sleep(3)
            # get active user number
            active_user = driver.find_elements_by_css_selector(".Text-wvugs1-0.Summary__SectionBody-tv96kb-2"
                                                        ".gboEcw.Summary__MetricWrapper.summary-value")[2]
            #output for G - R columns
            worksheet_DB.update_cell(lastrow1, column_count, download.text)
            worksheet_DB.update_cell(lastrow1, column_count + 6, active_user.text)
            column_count = column_count + 1
            print(str(column_count) + ": DL : " + download.text + " active: " + active_user.text)

def get_categorys(lastrow1):

    # column T, U, V
    game_category = "Non game"
    game_sub = "Non game"
    game_sub2 = "Non game"
    try:
        xpath1 = "//*[@id=\"__next\"]/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[4]/div/a[1]"
        game_category = driver.find_element_by_xpath(xpath1).text
        print(game_category)
        game_category = game_category[7:]
        try:
            xpath2 = "//*[@id=\"__next\"]/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[4]/div/a[2]"
            game_sub = driver.find_element_by_xpath(xpath2).text
            game_sub = game_sub[7:]
            try:
                xpath3 = "//*[@id=\"__next\"]/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[4]/div/a[3]"
                game_sub2 = driver.find_element_by_xpath(xpath3).text
                game_sub2 = game_sub2[10:]
            except:
                game_sub2 = None
        except:
            game_sub = None
    except:
        print("not getting game")
        game_category = None


    # column S, W
    selectors = [".Tooltip__ContentWrapper-yao88u-0.iNrEnu.underline", "#__next > div.flexview__FlexView-sc-15q74yn-0.v1__PageWrapper-sc-1uzwsep-2.habsls.PageLayout__PageContent.screenshotBot-target.FlexView > div.flexview__FlexView-sc-15q74yn-0.v1__PageContent-sc-1uzwsep-3.hgwpFd.FlexView > div.flexview__FlexView-sc-15q74yn-0.fiyEPn.PageLayoutMainBody.FlexView > div > div.flexview__FlexView-sc-15q74yn-0.geHbeU.FlexView > div.PageLayoutWithSubSidebar__Content-ekpd99-1.gZQvYQ > div.flexview__FlexView-sc-15q74yn-0.ReportLayout__DataWrapper-mvukfq-1.coHTvR.FlexView > div.details__GridContainer-icuvxq-0.edwOwq > div.details__GridRow-icuvxq-1.details__GridSideSection-icuvxq-3.eWqnLQ > div.details__GridRow-icuvxq-1.details__GridSide1Section-icuvxq-4.kzNQmy > div:nth-child(3) > ul > li:nth-child(1) > div > span"]
    contents = []
    for selector in selectors:
        try:
            content = driver.find_element_by_css_selector(selector).text
            contents.append(content)
        except:
            pass
    try:
        category = contents[0]
    except:
        category = None
    try:
        last_update = contents[1]
    except:
        last_update = None



    output_list = [category, game_category, game_sub, game_sub2, last_update]
    for j in range(len(output_list)):
        try:
            worksheet_DB.update_cell(lastrow1, j+19, output_list[j])
        except:
            worksheet_DB.update_cell(lastrow1, j+19, "N/A")


def get_detail_infos():
    # get dict for About info, column X, Y, Z, AA

    cur_url = driver.current_url
    headers_dic = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
    try:
        res = requests.get(cur_url, timeout=(12.0, 12.5), headers=headers_dic)
        #res = requests.get(r"https://www.appannie.com/haeders", timeout=(12.0, 12.5))
        res.raise_for_status()
    except:
        print("time out")
    print(cur_url)
    time_elapsed = res.elapsed.total_seconds()
    print(res.status_code)
    print('time_elapsed:', time_elapsed)
    sleep(5)
    soup = BeautifulSoup(res.text, 'lxml')
    title_text = soup.find('title').get_text()
    print(title_text)
    about = {}
    elems = soup.find_all("h1")
    print(elems)
    for tag in soup.find_all(['dt', 'dd']):
        print(tag)
        if tag.name == 'dt':
           key = tag.get_text()
        elif tag.name == 'dd':
            about[key] = tag.get_text()
    print(about)
    HQ = about["Company HQ"]
    lang = about["Languages"]
    requirement = about["Requirement"]
    size = about["Size"]

    # output for S-AA
    output_list = [HQ, lang, requirement, size]
    for j in range(len(output_list)):
        try:
            worksheet_DB.update_cell(lastrow1, j+25, output_list[j])
        except:
            worksheet_DB.update_cell(lastrow1, j+25, "N/A")






default()
main()
driver.close()
driver.quit()




















