from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from dotenv import load_dotenv
from pathlib import Path
from api.db import get_db
import json
import os

#
# Load API Keys
#
load_dotenv(Path(".env"))
API_KEY = os.getenv("API_KEY")
SERVER_PREFIX = os.getenv("SERVER_PREFIX")

# Global Variables - TEMP
LIST_ID_PA = "4b890a1b03" # Country - Audience - Panamá
LIST_ID_CO = "cae142989c" # Country - Audience - Colombia
LIST_ID_CR = "061656a504" # Country - Audience - Costa Rica
GROUP_ID_PA = "383283a2bd" # group ID of interests - Panama
GROUP_ID_CO = "cb260f02fa" # group ID of interests - Panama
GROUP_ID_CR = "" # group ID of interests - Panama

bp = Blueprint("forms", __name__)

@bp.route("/")
def index():
    """Show home page for Customer DB"""
    return render_template("forms/index.html")


@bp.route("/panama", methods=("GET", "POST"))
def panama():
    """Transacctional Data for Customers"""
    my_brands = get_brands(LIST_ID_PA, GROUP_ID_PA)
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
      sisley_specific = ";".join(request.form.getlist("sisley-specific"))
      adp_specific = ";".join(request.form.getlist("adp-specific"))
      payot_specific = ";".join(request.form.getlist("payot-specific"))
      phyto_specific = ";".join(request.form.getlist("phyto-specific"))
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
                     state, interests, guerlain_specific, sisley_specific,
                     adp_specific, payot_specific, phyto_specific, notas)


    return render_template("forms/panama.html", my_brands=my_brands, beauty_advisors=beauty_advisors, stores=stores)


@bp.route("/colombia", methods=("GET", "POST"))
def colombia():
    """Transacctional Data for Customers"""
    my_brands = get_brands(LIST_ID_CO, GROUP_ID_CO)
    db = get_db()
    beauty_advisors = db.execute(
        "SELECT fullname FROM CONSEJERAS WHERE subsidiaryid = '2'"
    ).fetchall()
    stores = db.execute(
        "SELECT storename FROM TIENDAS WHERE subsidiaryid = '2'"
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
      sisley_specific = ";".join(request.form.getlist("sisley-specific"))
      adp_specific = ";".join(request.form.getlist("adp-specific"))
      payot_specific = ";".join(request.form.getlist("payot-specific"))
      phyto_specific = ";".join(request.form.getlist("phyto-specific"))
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
        add_customer(LIST_ID_CO, email_address, first_name, last_name,
                     phone, birth_day, gender, store, advisor, country,
                     state, interests, guerlain_specific, sisley_specific,
                     adp_specific, payot_specific, phyto_specific, notas)


    return render_template("forms/colombia.html", my_brands=my_brands, beauty_advisors=beauty_advisors, stores=stores)

"""
Mailchimp API functions
"""
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from datetime import datetime


def add_customer(list_id:str, email:str,first_name:str, last_name:str, phone:str, bday:str,
                 gender:str, store:str, beauty_advisor:str, country:str,
                 state:str, brands:dict, guerlain_specific:str, sisley_specific:str,
                 adp_specific:str, payot_specific:str, phyto_specific:str, notes:str):
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
          "SISLEY": sisley_specific,
          "ADP": adp_specific,
          "PAYOT": payot_specific,
          "PHYTO": phyto_specific

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
    print(f"{email}:\n{json.dumps(error_json, indent=2)}")


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
