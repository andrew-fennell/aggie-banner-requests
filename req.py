import time
import json
import requests
import os
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options



#======================== HOW TO CONSTRUCT 'TERM' ========================#
"""
YEAR + SEMESTER + LOCATION

YEAR = 4 digit year         ie. 2020
SEMESTER = 
    Spring = 1
    Summer = 2
    Fall = 3

Location = 
    College Station = 1
    Galveston = 2
    Qatar = 3
    Half year = 4      (not sure where this is needed yet)


EXAMPLES:
2018 Summer in Galvestor: term = 201822
2016 Spring in Qatar: term = 201613
2020 Fall in College Station: term = 202031
"""

#============================ GLOBAL VARIABLES ============================#

base_url = 'compassxe-ssb.tamu.edu'
subjects = [
    'ACCT', 'AEGD', 'AERO', 'AERS', 'AFST', 'AGCJ', 'AGEC', 'AGLS', 'AGSC', 'AGSM', 'ALEC', 'ALED', 'ANSC', 'ANTH',
    'ARAB', 'ARCH', 'AREN', 'ARTS', 'ASCC', 'ASTR', 'ATMO', 'ATTR', 'BAEN', 'BEFB', 'BESC', 'BICH', 'BIED', 'BIMS',
    'BIOL', 'BIOT', 'BMEN', 'BUAD', 'BUSH', 'BUSN', 'CARC', 'CEHD', 'CHEM', 'CHEN', 'CHIN', 'CLAS', 'CLBA', 'CLEN',
    'CLGE', 'CLSC', 'COMM', 'COSC', 'CPSY', 'CSCE', 'CVEN', 'DASC', 'DCED', 'DDHS', 'DPHS', 'ECEN', 'ECMT', 'ECON',
    'EDAD', 'EDCI', 'EDHP', 'EDTC', 'EEBL', 'EHRD', 'ENDO', 'ENDS', 'ENGL', 'ENGR', 'ENTC', 'ENTO', 'EPFB', 'EPSY',
    'ESET', 'ESSM', 'EURO', 'EVEN', 'FILM', 'FINC', 'FIVS', 'FREN', 'FYEX', 'GENE', 'GEOG', 'GEOL', 'GEOP', 'GEOS',
    'GERM', 'HCPI', 'HEFB', 'HISP', 'HIST', 'HLTH', 'HORT', 'HPCH', 'IBST', 'IBUS', 'ICPE', 'IDIS', 'INST', 'INTA',
    'INTS', 'ISEN', 'ISTM', 'ITAL', 'ITDE', 'JAPN', 'JOUR', 'KINE', 'KNFB', 'LAND', 'LAW', 'LBAR', 'LBEV', 'LING',
    'LMAS', 'MASC', 'MATH', 'MEEN', 'MEFB', 'MEMA', 'MEPS', 'MGMT', 'MKTG', 'MLSC', 'MMET', 'MPHY', 'MPIM', 'MSCI',
    'MSEN', 'MUSC', 'MUST', 'MXET', 'NEXT', 'NFSC', 'NRSC', 'NURS', 'NVSC', 'OBIO', 'OCEN', 'OCNG', 'OMFP', 'OMFR',
    'OMFS', 'ORTH', 'PEDD', 'PERF', 'PERI', 'PETE', 'PHAR', 'PHEB', 'PHEO', 'PHIL', 'PHLT', 'PHPM', 'PHSC', 'PHYS',
    'PLAN', 'PLPA', 'POLS', 'POSC', 'PROS', 'PSAA', 'PSYC', 'RDNG', 'RELS', 'RENR', 'RPTS', 'RUSS', 'SABR', 'SCEN',
    'SCMT', 'SEFB', 'SENG', 'SOCI', 'SOMS', 'SOPH', 'SPAN', 'SPED', 'SPMT', 'SPSY', 'STAT', 'TAMU', 'TCMG', 'TCMT',
    'TEED', 'TEFB', 'THAR', 'UGST', 'URPN', 'URSC', 'VIBS', 'VIST', 'VIZA', 'VLCS', 'VMID', 'VPAT', 'VSCS', 'VTMI',
    'VTPB', 'VTPP', 'WFSC', 'WGST', 'WMHS'
]

def CompassConstructSearch(dept, course, sessionID, term, pageMaxSize=1000):
    '''Constructs search request url given the inputs.'''
    # Base Compass URL
    base_url = 'compassxe-ssb.tamu.edu'

    # Search URL
    url = 'https://{}/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_subject={}&txt_courseNumber={}&txt_term={}&startDatepicker=&endDatepicker=&uniqueSessionId={}&pageOffset=0&pageMaxSize={}&sortColumn=subjectDescription&sortDirection=asc'.format(base_url, dept, course, term, sessionID, pageMaxSize)

    return url

def start_session():
    '''
    Starts and prepares session for searches.
    This uses selenium to start the session and verify the uniqueSessionID
    that is required for searches. It then switches to a requests session.
    '''
    # Open Headless Selenium
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    s = webdriver.Chrome('C:/Users/Andrew/projects/agreq/chromedriver.exe', options=chrome_options)

    # Load page to initialize session
    s.get('https://{}/StudentRegistrationSsb/ssb/term/termSelection?mode=search'.format(base_url))
    #time.sleep(3)

    # Navigating webpage
    term_area = s.find_element_by_class_name('select2-container')
    term_area.click()

    text_area = s.find_element_by_id('s2id_autogen1_search')
    text_area.send_keys("Fall 2020 - College Station")
    time.sleep(2)
    text_area.send_keys(Keys.ENTER)

    btn = s.find_element_by_xpath('//*[@id="term-go"]')
    btn.click()

    # Use javascript in Chrome console to scrape unique session id from session storage
    javascript = "session_id = window.sessionStorage['xe.unique.session.storage.id']"
    s.execute_script(javascript)

    # Make unique session id into a cookie
    javascript = "document.cookie = 'sid=' + session_id"
    s.execute_script(javascript)

    # Take sessionID cookie and store it in python variable
    sessionID = s.get_cookie('sid')['value']

    # Transfering selenium session to requests session
    headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    }

    session = requests.session()
    session.headers.update(headers)

    for cookie in s.get_cookies():
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    return session, sessionID

def reset_search(session):
    '''Resets search so a new search request can be made'''
    # reset search
    r = session.post('https://{}/StudentRegistrationSsb/ssb/classSearch/resetDataForm'.format(base_url))
    print("Search reset.")
    print()
    return r.status_code

def search(session, sessionID, dept, course, term):
    '''Sends search request to and returns the data'''
    resp = session.get(CompassConstructSearch(dept, course, sessionID, term))
    data = resp.json()['data']

    return data

def write_data(outfile, course_data):
    '''Takes course data and writes it to txt file'''
    outfile.write("courseTitle: " + str(course_data['courseTitle']) + '\n')
    outfile.write("subject: " + str(course_data['subject']) + '\n')
    outfile.write("courseNumber: " + str(course_data['courseNumber']) + '\n')
    outfile.write("sequenceNumber: " + str(course_data['sequenceNumber']) + '\n')
    outfile.write("id: " + str(course_data['id']) + '\n')
    outfile.write("term: " + str(course_data['term']) + '\n')
    outfile.write("campusDescription: " + str(course_data['campusDescription']) + '\n')
    outfile.write("maximumEnrollment: " + str(course_data['maximumEnrollment']) + '\n')
    outfile.write("enrollment: " + str(course_data['enrollment']) + '\n')
    outfile.write("seatsAvailable: " + str(course_data['seatsAvailable']) + '\n')
    outfile.write('\n')

def make_course_json(course_data):
    '''Takes course data and returns object that can be written to a json file'''
    x = {
        "courseTitle": str(course_data['courseTitle']),
        "subject": str(course_data['subject']),
        "courseNumber": str(course_data['courseNumber']),
        "sequenceNumber": str(course_data['sequenceNumber']),
        "id": str(course_data['id']),
        "term": str(course_data['term']),
        "campusDescription": str(course_data['campusDescription']),
        "maximumEnrollment": str(course_data['maximumEnrollment']),
        "enrollment": str(course_data['enrollment']),
        "seatsAvailable": str(course_data['seatsAvailable']),
    }

    return x

def write_json(department, data):
    json_data = {}
    json_data['course'] = []
    prev = str(data[0]['courseNumber'])
    for x in data:
        
        current = str(x['courseNumber'])
        if prev != current:
            with open('courses/' + department + "/" + prev + ".json", 'w+') as outfile:
                json.dump(json_data['course'], outfile)

            prev = current
            json_data['course'] = []
            
        json_data['course'].append(make_course_json(x))
    

def get_all_courses(session, sessionID, term):
    '''
    This function will scrape all course data for all departments/subjects. 
    This will take longer to execute and should not be ran very often.
    '''
    
    for department in subjects:
        
        reset_search(session)

        # Make requests for department data
        print()
        print("Getting Data for " + department)
        data = search(session, sessionID, department, '', '202031')
        print()
        
        # Write data to file to courses/{department}/{courseNumber}.json
        if data:
            prev = str(data[0]['courseNumber'])
            outfile = open('courses/' + department + "/" + prev + ".json", 'w+')
            for x in data:

                current = str(x['courseNumber'])
                if prev != current:
                    outfile.close()
                    prev = current
                    outfile = open('courses/' + department + "/" + prev + ".json", 'w+')
                    
                write_data(outfile, x)

            print("Data Retrieved for " + department)
        else:
            print("No data for " + department)
    
    print("All data retrieved.")

def get_department(session, sessionID, department, term):
    '''
    This function scrapes the data for one department. This will
    update all course data for the department entered.
    '''
    
    reset_search(session)

    # Make requests for department data
    print("Getting Data for " + department)
    data = search(session, sessionID, department, '', '202031')
    
    
    # Write data to file to courses/{department}/{courseNumber}.txt
    if data:
        prev = str(data[0]['courseNumber'])
        outfile = open('courses/' + department + "/" + prev + ".json", 'w+')
        for x in data:
            current = str(x['courseNumber'])
            if prev != current:
                outfile.close()
                prev = current
                outfile = open('courses/' + department + "/" + prev + ".json", 'w+')
                
            write_data(outfile, x)

        print("Data Retrieved for " + department)
    else:
        print("No data for " + department)

def get_course(session, sessionID, department, course, term):
    '''
    This function scrapes the data for one course. 
    This will update data for all sections of one course
    '''
    
    reset_search(session)

    # Make requests for department data
    print()
    print("Getting Data for " + department + course)
    data = search(session, sessionID, department, course, '202031')
    print()
    
    json_data = {}
    json_data['course'] = []
    # Write data to file to courses/{department}/{courseNumber}.json
    if data:
        prev = str(data[0]['courseNumber'])
        for x in data:
            
            current = str(x['courseNumber'])
            if prev != current:
                with open('courses/' + department + "/" + prev + ".json", 'w+') as outfile:
                    json.dump(json_data['course'], outfile)

                prev = current
                json_data['course'] = []
                
            json_data['course'].append(make_course_json(x))
            

        print("Data Retrieved for " + department + course)
    else:
        print("No data for " + department + course)

def startDB():
    print("Starting MongoDB...")
    client = MongoClient('localhost', 27017)
    db = client['agreq']
    collection_course = db['course']
    print()

    return client, collection_course

#def dataToDB():
#    for dept in subjects:

def makeFolders():
    return

def main():
    
    # Start session
    session, sessionID = start_session()

    term = '202031' # 2020 3 1 where 2020 is year, 3 is fall, 1 is location

    #get_all_courses(session, sessionID, term)               # Example of getting ALL data
    #get_department(session, sessionID, 'CSCE', term)         # Example of getting one department's data
    get_course(session, sessionID, 'CSCE', '121', term)     # Example of getting one course's data


    # Threading to collect data from ALL courses quicker... It might be a sloppy solution though
    """
    processes = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for dept in subjects:
            processes.append(executor.submit(get_department, session, sessionID, dept, term))

    print("\n========================\n")
    """
    
    #client, collection_course = startDB()

    #directory = r'C:\Users\Andrew\projects\agreq\courses'

    #for subdir, dirs, files in os.walk(directory):
    #   for filename in files:
     #       if filename.endswith('.json'):
      #          
       #         with open(r'{}\{}'.format(subdir,filename)) as file: 
        #            file_data = json.load(file)
         #       
          #      if file_data:
           #         if isinstance(file_data, list): 
            #            collection_course.insert_many(file_data)   
             #       else: 
              #          collection_course.insert_one(file_data) 

    #client.close()

main()