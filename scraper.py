# scraper.py
import requests
from bs4 import BeautifulSoup
import warnings
import re
import datetime
from dateutil.parser import parse as parse_date

from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

BASE_URL = "https://app.ktu.edu.in"
REQUEST_TIMEOUT = (5, 15) 

def create_error_response(username, message):
    # ... (no change in this function)
    return {
        "status": "error",
        "request_info": {
            "username": username,
            "timestamp": datetime.datetime.now().isoformat()
        },
        "error_message": message
    }

def clean_key(text):
    # ... (no change in this function)
    return text.strip().replace(' ', '_').replace('/', '_').lower()

def extract_details_from_list(container, key_map=None):
    # ... (no change in this function)
    data = {}
    if not container:
        return data
    if key_map is None: key_map = {}
    for li in container.find_all('li', class_='list-group-item'):
        badge = li.find('span', class_='view-badge')
        if badge:
            key_text = badge.text.strip()
            key = key_map.get(key_text, clean_key(key_text))
            value = badge.next_sibling.strip() if badge.next_sibling and badge.next_sibling.string else ''
            if not value and li.find('a'):
                value = li.find('a').get_text(strip=True)
            data[key] = value.strip()
    return data

def scrape_ktu_data(username, password):
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/50 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': f'{BASE_URL}/login.htm'
    }
    session.headers.update(headers)
    
    LOGIN_URL = f"{BASE_URL}/login.htm"
    PROFILE_URL = f"{BASE_URL}/eu/stu/studentDetailsView.htm"

    try:
        # --- LOGIN LOGIC ---
        print("Step 1: Visiting login page to get CSRF token...")
        login_page_response = session.get(LOGIN_URL, verify=False, timeout=REQUEST_TIMEOUT) 
        login_page_response.raise_for_status()
        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        csrf_token_tag = soup.find('input', {'name': 'CSRF_TOKEN'})
        if not csrf_token_tag:
            return create_error_response(username, "Could not find CSRF token on login page.")
        csrf_token = csrf_token_tag['value']
        print(f"Found CSRF Token: {csrf_token[:10]}...") 

        print("Step 2: Sending POST request to log in...")
        login_payload = { 'username': username, 'password': password, 'CSRF_TOKEN': csrf_token }
        login_response = session.post(LOGIN_URL, data=login_payload, verify=False, timeout=REQUEST_TIMEOUT)
        login_response.raise_for_status()

        if "Invalid username or password!" in login_response.text:
            return create_error_response(username, "Login failed. Either username or password is wrong, please check your credentials.")
        
        # This print statement was moved from here.

        print(f"Step 3: Scraping FULL profile page...")
        profile_page_response = session.get(PROFILE_URL, verify=False, timeout=REQUEST_TIMEOUT)
        profile_page_response.raise_for_status()
        profile_soup = BeautifulSoup(profile_page_response.text, 'html.parser')

        # --- DATA EXTRACTION ---
        
        personal_tab = profile_soup.find('div', id='personalTab_personal')
        if not personal_tab:
            return create_error_response(username, "Login failed. Either username or password is wrong, please check your credentials.")

        # --- CHANGED: Moved the "Login Successful!" message here ---
        # It is only truly successful AFTER we confirm we can see the profile page.
        print("Login Successful!")

        result = {
            "request_info": {"timestamp": datetime.datetime.now().isoformat(), "username": username},
            "personal": {}, "admission_details": {}, "contact_details": {},
            "bank_account_details": {}, "qualification_details": {}, "guardian_details": {},
            "curriculum": {"general": {}, "semesters": {}},
            "any_other_data_related_to_api_call_or_anything": {}
        }
        
        # ... (Rest of the scraping code is unchanged) ...
        panel_title_tag = profile_soup.find('h3', class_='panel-title')
        if panel_title_tag:
            full_title_text = panel_title_tag.get_text(strip=True)
            student_name = full_title_text.split('(')[0].strip()
            result['personal']['name'] = student_name
        else:
            result['personal']['name'] = ""

        basic_details_container = personal_tab.find('div', class_='row')
        personal_data = extract_details_from_list(basic_details_container)
        if personal_data.get('date_of_birth'):
            try: personal_data['date_of_birth'] = parse_date(personal_data['date_of_birth']).strftime('%Y-%m-%d')
            except (ValueError, TypeError): pass
        result['personal'].update(personal_data)
        avatars = profile_soup.find('div', class_='useravatar')
        if avatars:
            images = avatars.find_all('img', class_='card-bkimg')
            if len(images) > 0 and images[0].get('src'): result['personal']['student_photo_link'] = BASE_URL + images[0]['src']
            if len(images) > 1 and images[1].get('src'): result['personal']['student_signature_link'] = BASE_URL + images[1]['src']
        accordion = personal_tab.find('div', id='accordion')
        if accordion:
            admission_panel = accordion.find('div', id='collapseOne')
            result['admission_details'] = extract_details_from_list(admission_panel)
            contact_panel = accordion.find('div', id='collapseTwo')
            if contact_panel:
                well_text = contact_panel.find('div', class_='well').get_text(separator=' ', strip=True)
                mobile_match = re.search(r'Mobile:\s*([\d\s]+)', well_text)
                email_match = re.search(r'Email:\s*([\w.@]+)', well_text)
                landline_match = re.search(r'LandLine:\s*([\d\s]*)', well_text)
                result['contact_details']['mobile'] = mobile_match.group(1).strip() if mobile_match else ""
                result['contact_details']['email'] = email_match.group(1).strip() if email_match else ""
                result['contact_details']['landline'] = landline_match.group(1).strip() if landline_match else ""
                addresses = contact_panel.find_all('div', class_='col-sm-5')
                if len(addresses) >= 2:
                    result['contact_details']['communication_address'] = ' '.join(addresses[0].stripped_strings).replace('Communication Address', '').strip()
                    result['contact_details']['permanent_address'] = ' '.join(addresses[1].stripped_strings).replace('Permanent Address', '').strip()
            bank_panel = accordion.find('div', id='collapseEight')
            result['bank_account_details'] = extract_details_from_list(bank_panel)
            qual_panel = accordion.find('div', id='collapseThree')
            result['qualification_details'] = extract_details_from_list(qual_panel)
            if qual_panel:
                cert_table = qual_panel.find('table')
                if cert_table:
                    for row in cert_table.find('tbody').find_all('tr'):
                        cols = row.find_all('td')
                        if len(cols) == 3:
                            doc_type_span = cols[0].find('span', class_='view-badge')
                            link_tag = cols[2].find('a', href=re.compile(r'download=file'))
                            if doc_type_span and link_tag:
                                doc_type = clean_key(doc_type_span.text) + "_link"
                                result['qualification_details'][doc_type] = BASE_URL + link_tag['href']
            guardian_panel = accordion.find('div', id='collapseFive')
            if guardian_panel:
                for col in guardian_panel.find_all('div', class_='col-sm-4'):
                    title_tag = col.find('li', class_='list-group-item-success')
                    if title_tag:
                        guardian_type = title_tag.text.strip().lower()
                        result['guardian_details'][guardian_type] = extract_details_from_list(col)

        curriculum_tab = profile_soup.find('div', id='curriculamTab_curriculam')
        if curriculum_tab:
            details_list = curriculum_tab.find('ul', class_='list-group')
            if details_list:
                for li in details_list.find_all('li', class_='list-group-item'):
                    badge = li.find('span', class_='view-badge')
                    if badge and badge.next_sibling:
                        key_text = badge.text.strip()
                        value_text = badge.next_sibling.strip()
                        if "Current Semester" in key_text:
                            result['curriculum']['general']['current_semester'] = value_text
                        elif "CGPA" in key_text:
                            result['curriculum']['general']['total_cgpa'] = value_text
            
            for panel in curriculum_tab.find_all('div', class_='panel-default'):
                if panel.find('a', href='#collapseSix'): continue
                title_tag = panel.find('h5', class_='panel-title')
                if not title_tag: continue
                anchor_tag = title_tag.find('a')
                if not anchor_tag: continue
                
                sem_name_raw = anchor_tag.text.strip()
                sem_key_match = re.search(r'\d+', sem_name_raw)
                if not sem_key_match: continue
                sem_key = "s" + sem_key_match.group()
                
                courses, sgpa = [], "N/A"
                table = panel.find('table')
                if table and table.find('tbody'):
                    rows = table.find('tbody').find_all('tr')
                    for i, row in enumerate(rows):
                        cols = [td.get_text(separator=' ', strip=True) for td in row.find_all('td')]
                        if len(cols) < 9: continue
                        
                        course_raw = cols[1]
                        code_match = re.match(r'([A-Z0-9]+)\s*-\s*(.*)', course_raw)
                        
                        # Clean slot field: strip extra whitespace and normalize
                        slot_cleaned = ' '.join(cols[0].split())
                        
                        courses.append({
                            "slot": slot_cleaned, "course_code": code_match.group(1) if code_match else "N/A",
                            "course_name": code_match.group(2) if code_match else course_raw,
                            "course_credit": cols[2], "course_valuation_type": cols[3],
                            "completed_status": cols[4], "is_eligible_for_written_exam": cols[5],
                            "grade": cols[7], "earned_credit": cols[8],
                            "examination_details": cols[9] if len(cols) > 9 else ""
                        })

                        if i == 0 and len(cols) > 10 and cols[10]:
                            sgpa = cols[10]

                result['curriculum']['semesters'][sem_key] = {"sgpa": sgpa, "courses": courses}

        result['request_info']['status'] = 'success'
        return result

    except requests.exceptions.Timeout:
        return create_error_response(username, "The request to the KTU server timed out. The server is likely down or blocking automated requests.")
    except requests.exceptions.RequestException as e:
        return create_error_response(username, f"A network error occurred: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return create_error_response(username, f"An unexpected error occurred during scraping: {e}")