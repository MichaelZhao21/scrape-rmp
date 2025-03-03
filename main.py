from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import dotenv
import os
import time
import re
import requests
import json

# Load the environment variables
dotenv.load_dotenv()

def get_headers():
    # Set up Selenium to use Chrome
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--headless")
        # chrome_options.add_experimental_option("detach", True)  # Keeps the browser window open
        service = Service("./chromedriver")  # Specify the path to your chromedriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(2)

    except Exception as e:
        print(f"Failed to start the Chrome driver: {e}")
        print("Go to https://googlechromelabs.github.io/chrome-for-testing/#stable to download the latest version of ChromeDriver. Copy the executable to the root folder of this project. You may also need the latest version of Chrome; make sure your chrome is updated.")
        exit(1)

    # Get the school ID
    school_id = os.environ["SCHOOL_ID"]

    # Open the rmp website
    try:
        driver.get(f'https://www.ratemyprofessors.com/search/professors/{school_id}?q=*')
    except TimeoutException:
        driver.execute_script("window.stop();")
        print('bruh')
        try:
            driver.refresh()
        except TimeoutException:
            driver.execute_script("window.stop();")
        time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "CCPAModal__StyledCloseButton-sc-10x9kq-2"))
        )
        close_button = driver.find_element(By.CLASS_NAME, "CCPAModal__StyledCloseButton-sc-10x9kq-2")
        driver.execute_script("arguments[0].click();", close_button)
        print("Cookie popup closed.")
        time.sleep(2)
    except Exception as e:
        print("No cookie popup found or issue clicking it:", e)

    try:
        # Wait for a button whose class name contains "Pagination" and click it
        pagination_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "PaginationButton__StyledPaginationButton-txi1dr-1"))
        )
        driver.execute_script("arguments[0].click();", pagination_button)
        print("Clicked on the pagination button.")

    except Exception as e:
        print(f"Failed to find or click the pagination button: {e}")

    time.sleep(4)

    # Capture and print request headers for a specific domain
    # print(driver.requests)
    url_filter = "ratemyprofessors.com/graphql"
    graphql_headers = {}
    for request in driver.requests:
        if url_filter in request.url:
            print(f"\n[REQUEST] {request.url}")

            # Get request body as string
            request_body = request.body
            m = re.findall(r'schoolID":"(.*?)"', str(request_body))
            if m:
                print(f"\tschoolID: {m[0]}")
                school_id = m[0]
            else:
                print("schoolID not found in request body.")
                exit(1)
            
            print("Headers:")
            graphql_headers = request.headers
            for header, value in request.headers.items():
                print(f"\t{header}: {value}")
            print("-" * 50)

    driver.quit()
    return graphql_headers, school_id

def main():
    headers, id = get_headers()
    # headers = {
    #     'content-length':  '1282',
    #     'x-rmp-comp-id':  '',
    #     'sec-ch-ua-platform':  '"Linux"',
    #     'authorization':  'Basic dGVzdDp0ZXN0',
    #     'user-agent':  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/133.0.0.0 Safari/537.36',
    #     'sec-ch-ua':  'Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133',
    #     'content-type':  'application/json',
    #     'sec-ch-ua-mobile':  '?0',
    #     'accept':  '*/*',
    #     'origin':  'https://www.ratemyprofessors.com',
    #     'sec-fetch-site':  'same-origin',
    #     'sec-fetch-mode':  'cors',
    #     'sec-fetch-dest':  'empty',
    #     'referer':  'https://www.ratemyprofessors.com/search/professors/1273?q=*',
    #     'accept-encoding':  'gzip, deflate, br, zstd',
    #     'accept-language':  'en-US,en;q=0.9',
    #     'priority':  'u=1, i',
    #     'cookie':  'RMP_AUTH_COOKIE_VERSION=v01; _pubcid=6cb75d77-139d-41e6-bc03-8c52a5cbe6f3; _pubcid_cst=zix7LPQsHA%3D%3D; _ga=GA1.1.745869951.1741030785; pjs-unifiedid=%7B%22TDID%22%3A%22e19492c0-0d0c-4747-9da7-c3b61b518f85%22%2C%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222025-03-03T19%3A39%3A45%22%7D; pjs-unifiedid_cst=zix7LPQsHA%3D%3D; _ga_WET17VWCJ3=GS1.1.1741030785.1.1.1741030786.0.0.0; lotame_domain_check=ratemyprofessors.com; _cc_id=c45c903c4b858c32eafa6c7a5286a6af; panoramaId_expiry=1741117186477; cto_bundle=czjSLF9JJTJCdWt2dXd3dG9vS2UxMHRxN25xSmppcWpCOFBFOXZyazNxUFRIUU1zM2JSZmw1d0hDZElFUmd3M2lsaVIlMkZmdVYwNHk1VlhRRGlkRjJ0UGNycyUyRlFhY3Mzc1JaZ25QdkhtR29VbjdrWFNwJTJGblVsZVBGZ0c5dlhwQUViaXBlSUly; cto_bidid=qkG0El95T0NWeWt5VkJGbVoxVm1QeklTYW9CSHhSR2xsRyUyRjhReDJzSjJZMSUyRllJSWVnNGxubmtldklwcEtkdUJPNVQlMkJITXF3TXN4RCUyQmh5RTR5ZUp1WXFoMDFoajdJOG5rVEFOSVY0OENjZGRpRGdFJTNE; _au_1d=AU1D-0100-001741030787-T9V1SYQ8-NO2H; FCNEC=%5B%5B%22AKsRol-eXLPbW3tPdEqeD39S52CkbQztVJSB4Sa7pUPmuebSMcYavnSb4WKHAppnI_uNYPu56ywJizfKZMfiZi6murTCw03ZuT_7_wgxFMEZxBRlFMvqh639wd1ZodSUTX9_AZSbKQ044ThAR7kmYKzxV9QXP9noIQ%3D%3D%22%5D%5D; __gads=ID=295faf21b7d0b92d:T=1741030788:RT=1741030788:S=ALNI_MZDQylvK-TTCmF8ZAMRqQhw6T5l4g; __gpi=UID=000010640e72111b:T=1741030788:RT=1741030788:S=ALNI_MbxsIwX64OYTjgD54bfS0YI9FEbiQ; __eoi=ID=f9277d8c468133c7:T=1741030788:RT=1741030788:S=AA-AfjZ2q8qh7_r2GJK067Sjx24v; ccpa-notice-viewed-02=true',
    # }
    # id = 'U2Nob29sLTEyNzM='

    req_data = {
        "query": """query TeacherSearchPaginationQuery( $count: Int!  $cursor: String $query: TeacherSearchQuery!) { search: newSearch { ...TeacherSearchPagination_search_1jWD3d } }
            fragment TeacherSearchPagination_search_1jWD3d on newSearch {
            teachers(query: $query, first: $count, after: $cursor) {
                didFallback
                edges {
                cursor
                node {
                    ...TeacherCard_teacher
                    id
                    __typename
                }
                }
                pageInfo {
                hasNextPage
                endCursor
                }
                resultCount
                filters {
                field
                options {
                    value
                    id
                }
                }
            }
            }

            fragment TeacherCard_teacher on Teacher {
            id
            legacyId
            avgRating
            numRatings
            courseCodes {    courseName    courseCount  }
            ...CardFeedback_teacher
            ...CardSchool_teacher
            ...CardName_teacher
            ...TeacherBookmark_teacher
            }

            fragment CardFeedback_teacher on Teacher {
            wouldTakeAgainPercent
            avgDifficulty
            }

            fragment CardSchool_teacher on Teacher {
            department
            school {
                name
                id
            }
            }

            fragment CardName_teacher on Teacher {
            firstName
            lastName
            }

            fragment TeacherBookmark_teacher on Teacher {
            id
            isSaved
        }""",
        "variables": {
            "count": 1000,
            "cursor": "",
            "query": {
                "text": "",
                "schoolID": id,
                "fallback": True
            }
        }
    }

    all_professors = []
    more = True
    while more:
        more = False
        # Make request to the graphql endpoint
        res = requests.post('https://www.ratemyprofessors.com/graphql', headers=headers, json=req_data)

        data = res.json()['data']['search']['teachers']['edges']
        professors = []
        for d in data:
            dn = d['node']
            professors.append({
                'firstName': dn['firstName'],
                'lastName': dn['lastName'],
                'department': dn['department'],
                'numRatings': dn['numRatings'],
                'avgDifficulty': dn['avgDifficulty'],
                'avgRating': dn['avgRating'],
                'wouldTakeAgainPercent': dn['wouldTakeAgainPercent'],
                'id': dn['id'],
                'legacyId': dn['legacyId'],
                'courseCodes': dn['courseCodes']
            })
        
        all_professors.extend(professors)
        print(f"Added {len(professors)} professors to the list. Total professors: {len(all_professors)}")
        if len(data) == 1000:
            req_data['variables']['cursor'] = data[len(data)-1]['cursor']
            more = True

    with open('professors.json', 'w') as f:
        json.dump(all_professors, f, indent=4)

    


if __name__ == "__main__":
    main()
