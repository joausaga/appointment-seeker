import logging
import time
import random

from notifier import notify_appointment
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.firefox.options import Options
from utils import get_config, normalize_text
from urllib3.connectionpool import log as urllibLogger


logging.basicConfig(
    filename='log/appointment_seeker.log', 
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s',
    datefmt='%d-%b-%y %H:%M'
)


# Turn off logging of Selenium and Urllib3
LOGGER.setLevel(logging.ERROR)
urllibLogger.setLevel(logging.ERROR)


def find_available_offices(config_params, appointment_data):
    available_offices = []

    # open browser
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    # open website
    browser.get(config_params['appointment_website'])
    
    # accept cookie message
    browser.find_element_by_id(
        config_params['page_1']['html_elements']['cookie_button_name']
    ).click()

    # select province and go to next page
    time.sleep(random.uniform(2, 4))
    province_list = Select(browser.find_element_by_name(
        config_params['page_1']['html_elements']['province_select_name'])
    )
    province_list.select_by_visible_text(
        appointment_data['province']
    )
    browser.find_element_by_id(
        config_params['page_1']['html_elements']['submit_button_name']
    ).click()

    # select dropdown lists
    hq_list = Select(browser.find_element_by_name(
        config_params['page_2']['html_elements']['office_select_name'])
    )
    # get list of offices
    offices = hq_list.options

    # iterate over offices
    for office in offices:
        if office.get_attribute('value') != '99':
            hq_list.select_by_value(office.get_attribute('value'))
            # wait a second to let procedure list to be filled
            time.sleep(1)
            # select procedure dropdown
            procedure_list = Select(browser.find_element_by_name(
                config_params['page_2']['html_elements']['procedure_select_name'])
            )
            # get office's procedures
            office_procedures = procedure_list.options
            # iterate over office' procedures
            for office_procedure in office_procedures:
                if office_procedure.get_attribute('value') != "-1":
                    if office_procedure.text == appointment_data['procedure'] and \
                       office.text not in appointment_data['offices_to_exclude']:
                        available_offices.append(office.text)
            time.sleep(random.uniform(1, 3))
    
    # sort by preference
    s_available_offices = []
    for preferred_office in appointment_data['preferred_offices']:
        if preferred_office in available_offices:
            s_available_offices.append(preferred_office)
    for available_office in available_offices:
        if available_office not in appointment_data['preferred_offices']:
            s_available_offices.append(available_office)

    # close browser
    browser.close()

    return s_available_offices


def check_no_appointments_msg(browser, msg_class_name, msg_text):
    elements = browser.find_elements_by_class_name(msg_class_name)
    for element in elements:
        if msg_text in element.text:
            return True
    return False


def seek_appointment():
    # load configuration parameters
    config_params = get_config('config.json')
    appointment_data = get_config('appointment_data.json')

    # get offices in which the procedure is available
    logging.info('##############')
    logging.info(f'Looking for offices in the provice of '\
                 f'{normalize_text(appointment_data["province"])} that offer the procedure '\
                 f'{normalize_text(appointment_data["procedure"])}')
    available_offices = find_available_offices(config_params, appointment_data)

    # open browser
    browser = webdriver.Firefox()
    # open website
    browser.get(config_params['appointment_website'])
    
    # 0. accept cookie message
    logging.info(f'Accepting cooking message\n')
    browser.find_element_by_id(
        config_params['page_1']['html_elements']['cookie_button_name']
    ).click()

    there_arent_appointments = False
    for office in available_offices:
        logging.info(f'Looking for appointments in office: {normalize_text(office)}')
        
        try:
            # 1. select province and go to next page
            time.sleep(random.uniform(1, 2))
            province_list = Select(browser.find_element_by_id(
                config_params['page_1']['html_elements']['province_select_name'])
            )
            province_list.select_by_visible_text(
                appointment_data['province']
            )
            browser.find_element_by_id(
                config_params['page_1']['html_elements']['submit_button_name']
            ).click()

            # 2. select office (sede), procedure (tramite), and go to next page
            time.sleep(random.uniform(1, 4))
            there_arent_appointments = check_no_appointments_msg(
                browser, 
                config_params['page_2']['html_elements']['msg_class_name'],
                config_params['page_2']['html_elements']['msg_text']
            )
            if there_arent_appointments:
                logging.info(f'There are not appointments at this moment in {normalize_text(office)}\n')
                continue
            office_list = Select(browser.find_element_by_name(
                config_params['page_2']['html_elements']['office_select_name'])
            )
            office_list.select_by_visible_text(office)
            procedure_list = Select(browser.find_element_by_name(
                config_params['page_2']['html_elements']['procedure_select_name'])
            )
            # we have to wait until the option is ready to be selected
            time.sleep(3)
            procedure_list.select_by_visible_text(appointment_data['procedure'])
            browser.find_element_by_id(
                config_params['page_2']['html_elements']['submit_button_name']
            ).click()

            # 3. enter into the procedure
            time.sleep(random.uniform(1, 2))
            browser.find_element_by_id(
                config_params['page_3']['html_elements']['submit_button_name']
            ).click()

            # 4. complete requester info go to the next page
            time.sleep(random.uniform(2, 6))
            input_element = browser.find_element_by_name(
                config_params['page_4']['html_elements']['nie_input_name']
            )
            input_element.send_keys(appointment_data['nie'])
            input_element = browser.find_element_by_name(
                config_params['page_4']['html_elements']['name_input_name']
            )
            input_element.send_keys(appointment_data['full_name'])
            country_list = Select(browser.find_element_by_name(
                config_params['page_4']['html_elements']['country_select_name'])
            )
            country_list.select_by_visible_text(
                appointment_data['country']
            )
            input_element = browser.find_element_by_name(
                config_params['page_4']['html_elements']['date_input_name']
            )
            input_element.send_keys(appointment_data['nie_expiration_date'])
            browser.find_element_by_id(
                config_params['page_4']['html_elements']['submit_button_name']
            ).click()

            # 5. click on "solicitar cita"
            time.sleep(random.uniform(1, 2))
            browser.find_element_by_id(
                config_params['page_5']['html_elements']['submit_button_name']
            ).click()

            # 6. check message and go back if there aren't appointments
            there_arent_appointments = check_no_appointments_msg(
                browser, 
                config_params['page_6']['html_elements']['msg_class_name'],
                config_params['page_6']['html_elements']['msg_text']
            )
            if there_arent_appointments:
                logging.info(f'There are not appointments for '\
                            f'{normalize_text(appointment_data["procedure"])} in {normalize_text(office)}\n')
                browser.find_element_by_id(
                    config_params['page_6']['html_elements']['exit_button_name']
                ).click()
            else:
                # 7. complete contact information of requester
                logging.info(f'Arrived to contact information page, we are close!')
                time.sleep(random.uniform(2, 4))
                input_element = browser.find_element_by_name(
                    config_params['page_7']['html_elements']['phone_input_name']
                )
                input_element.send_keys(appointment_data['phone_number'])
                input_element = browser.find_element_by_id(
                    config_params['page_7']['html_elements']['email_input_name']
                )
                input_element.send_keys(appointment_data['email'])
                input_element = browser.find_element_by_id(
                    config_params['page_7']['html_elements']['repeat_email_input_name']
                )
                input_element.send_keys(appointment_data['email'])
                browser.find_element_by_id(
                    config_params['page_7']['html_elements']['submit_button_name']
                ).click()

                # 8. check message and go back if there aren't appointments
                there_arent_appointments = check_no_appointments_msg(
                    browser, 
                    config_params['page_8']['html_elements']['msg_class_name'],
                    config_params['page_8']['html_elements']['msg_text']
                )
                if there_arent_appointments:
                    logging.info(f'There are not appointments for '\
                                f'{normalize_text(appointment_data["procedure"])} in {normalize_text(office)}\n')
                    browser.find_element_by_id(
                        config_params['page_8']['html_elements']['exit_button_name']
                    ).click()
                else:
                    logging.info('Found an appointment!, sending email')
                    notify_appointment(
                        config_params['sender_email_address'],
                        config_params['sender_email_password'],
                        config_params['email_host'],
                        config_params['email_host_port'],
                        appointment_data['email'],
                    )
                    break
        except Exception as e:
            logging.exception("Exception occurred")
    
    if there_arent_appointments:
        logging.info(f'Could not find appointments for '\
                     f'{normalize_text(appointment_data["procedure"])}\n')
        # close browser
        browser.close()

if __name__ == '__main__':
    seek_appointment()