import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from datetime import datetime
import json

# Global Variables - TEMP
API_KEY = "5bbae6a045509bde36148de97a935596-us21"
SERVER_PREFIX = "us21"
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
    print("\n", json.dumps(response, indent=2))

  except ApiClientError as error:
    print("Error: {}".format(error.text))


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


# add_customer(LIST_ID_PA, "psyko.killer@mp3.com", "John", "Connor", "61234567", "11/03", "Hombre", "Felix B. Maduro",
#              "Operador Panabel", "Panamá", "Veraguas", {"c5827d7605": True, "1b03a20f1c": True, "90ffce2501": True, "560c3d832b": True})


# Get List of brands
# my_brands = get_brands(LIST_ID_PA, "383283a2bd")
# print(json.dumps(my_brands, indent=2))
