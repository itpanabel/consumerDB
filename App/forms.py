from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from App.db import get_db
import json


bp = Blueprint("forms", __name__)

@bp.route("/")
def index():
    """Show home page for Customer DB"""
    return render_template("forms/index.html")


@bp.route("/panama", methods=("GET", "POST"))
def panama():
    """Transacctional Data for Customers"""
    LIST_ID_PA = "4b890a1b03" # Country - Audience - Panamá
    my_brands = get_brands(LIST_ID_PA, "383283a2bd")
    # print(json.dumps(my_brands, indent=2))
    db = get_db()
    beauty_advisors = db.execute(
        "SELECT fullname FROM CONSEJERAS WHERE subsidiaryid = '1'"
    ).fetchall()
    stores = db.execute(
        "SELECT storename FROM TIENDAS WHERE subsidiaryid = '1'"
    ).fetchall()
    error = None

    if request.method == "POST":
      email_address = request.form["email_address"]
      first_name = request.form["NOMBRE"]
      last_name = request.form["APELLIDO"]
      phone = request.form["TEL"]
      birth_day = request.form["BDAY"]
      gender = request.form["GENERO"]
      country = request.form["PAIS"]
      state = request.form["provincia"]
      store = request.form["TIENDA"]
      form_interests = request.form.getlist("interests")
      interests = {}
      guerlain_specific = ";".join(request.form.getlist("guerlain-specific"))
      advisor = request.form["CONSEJERA"]
      notas = request.form["notes"]
      if birth_day != "":
        tmp = birth_day.split("-")
        birth_day = f"{tmp[1]}/{tmp[2]}"
      for interest in form_interests:
        interests[interest] = True

      #
      # Add customer data to Mailchimp
      #
      if email_address != "":
        add_customer(LIST_ID_PA, email_address, first_name, last_name,
                     phone, birth_day, gender, store, advisor, country,
                     state, interests, guerlain_specific, notas)


    return render_template("forms/panama.html", my_brands=my_brands, beauty_advisors=beauty_advisors, stores=stores)



"""
Mailchimp API functions
"""
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from datetime import datetime

# Global Variables - TEMP
API_KEY = "5bbae6a045509bde36148de97a935596-us21"
SERVER_PREFIX = "us21"
#LIST_ID_PA = "4b890a1b03" # Country - Audience - Panamá
LIST_ID_CO = "" # Country - Audience - Colombia
LIST_ID_CR = "" # Country - Audience - Costa Rica


def add_customer(list_id:str, email:str,first_name:str, last_name:str, phone:str, bday:str,
                 gender:str, store:str, beauty_advisor:str, country:str,
                 state:str, brands:dict, guerlain_specific:list, notes:str):
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
          "NOTAS": notes,
          "GUERLAIN": guerlain_specific,
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
