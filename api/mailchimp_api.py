import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from datetime import datetime
import json

from dotenv import load_dotenv
from pathlib import Path
import os

#
# Load API Keys
#
load_dotenv(Path("secrets.env"))
API_KEY = os.getenv("API_KEY")
SERVER_PREFIX = os.getenv("SERVER_PREFIX")

# Global Variables - TEMP
LIST_ID_PA = "4b890a1b03" # Country - Audience - Panamá
LIST_ID_CO = "" # Country - Audience - Colombia
LIST_ID_CR = "" # Country - Audience - Costa Rica


def add_customer(list_id:str, email:str,first_name:str, last_name:str, phone:str, bday:str,
                 gender:str, store:str, beauty_advisor:str, country:str,
                 state:str, brands:dict):
  """This function create a new customer
  in Mailchimp Platform"""
  try:
    client = MailchimpMarketing.Client()
    client.set_config({
      "api_key": API_KEY,
      "server": SERVER_PREFIX
    })
    now = datetime.now()

    response = client.lists.add_list_member(list_id, {
      "email_address": email,
      "email_type": "html",
      "status": "subscribed",
      "merge_fields": {
          "NOMBRE": first_name,
          "APELLIDO": last_name,
          "TEL": phone,
          "BDAY": bday,
          "GENERO": gender,
          "TIENDA": store,
          "CONSEJERA": beauty_advisor,
          "PAIS": country,
          "LUGAR": state,
          "NOTAS": "",
          "GUERLAIN": "",
          "SISLEY": "",
          "ADP":"",
          "PAYOT": ""

      },
      "interests": brands,
      "timestamp_signup": now.strftime("%Y-%m-%d %H:%M:%S"),
      "language": "es",
      "vip": False,
      "marketing_permissions": [],
      "tags": []
      })
    # print("\n", json.dumps(response, indent=2))

  except ApiClientError as error:
    error_json = json.loads(error.text)
    log = open("error.log", "+a")
    log.write(f"{now} - {email}: {json.dumps(error_json)}\n")
    log.close()
    print(f"{email}:\n{json.dumps(error_json, indent=2)}\n")


def get_brands(list_id:str, group_id:str):
  """Obtain Brands for a Subsidiary
  @params:
    list_id:str """
  try:
    client = MailchimpMarketing.Client()
    client.set_config({
      "api_key": API_KEY,
      "server": SERVER_PREFIX
    })

    response = client.lists.list_interest_category_interests(list_id, group_id,count=30)
    data = response["interests"]
    brands = {}
    for item in data:
      key = item["id"]
      brands[key] = item["name"]
    return brands
  except ApiClientError as error:
    print("Error: {}".format(error.text))
