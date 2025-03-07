from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
from api.db import get_db
import hashlib
import json
import re
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
GROUP_ID_CO = "cb260f02fa" # group ID of interests - Colombia
GROUP_ID_CR = "" # group ID of interests - Costa Rica


bp = Blueprint("forms", __name__)


@bp.route("/")
def index():
    """Show home page for Customer DB"""
    return render_template("forms/index.html")


@bp.route("/testers-request", methods=("GET", "POST"))
def testers_request():
  db = get_db()
  subsidiaryCode = request.args.get("country")
  data = db.execute(f"SELECT T0.testercode, T0.tester_name, T1.brandname, T0.tester_axe FROM TESTERS T0 INNER JOIN MARCAS T1 WHERE T0.subsidiaryid = {subsidiaryCode}").fetchall()
  brands = db.execute(f"SELECT brandname FROM MARCAS WHERE subsidiaryid = {subsidiaryCode} ORDER BY brandname ASC").fetchall()
  beauty_advisors = db.execute(f"SELECT id, fullname FROM CONSEJERAS WHERE subsidiaryid = {subsidiaryCode}")
  pos = db.execute(f"SELECT id, pos_name FROM POS WHERE subsidiaryid = {subsidiaryCode} ORDER BY pos_name ASC")
  current_date = datetime.now()
  # para colombia el debe estar habilitado del 20-28 de cada mes.
  if int(subsidiaryCode) == 1:
    start_day = 1
    end_day = 8
  else:
    start_day = 15
    end_day = 28

  if current_date.day in range(start_day, end_day):
    if request.method == "POST":
      pdv = request.form["pos"]
      advisor = request.form["consejera"]
      itemCode = request.form.getlist("itemcode")
      orderedDate = datetime.now()
      try:
        for item in itemCode:
          db.execute(
            "INSERT INTO ORDEREDTESTERS (itemcode, orderdate, requester, orderpos, subsidiary) VALUES (?, ?, ?, ?, ?)",
            (item, orderedDate, advisor, pdv, subsidiaryCode)
          )
          db.commit()
          print(f"POS: {pdv}, consejera: {advisor} Articulos Solicitados: {item}, solicitado: {orderedDate.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        flash("Se envió su pedido exitosamente!\n Debe estarlo recibiendo el mes siguiente.", "alert-success")
      except db.IntegrityError:
        flash("Por favor contactar a soporte", "alert-warning")

    return render_template("forms/trequest.html", testers=data, brands=brands, beauty_advisors=beauty_advisors, pos=pos)

  return render_template("forms/bloqueado.html")



@bp.route("/panama", methods=("GET", "POST"))
def panama():
    """Transacctional Data for Customers"""
    my_brands = get_brands(LIST_ID_PA, GROUP_ID_PA)
    db = get_db()
    beauty_advisors = db.execute(
        "SELECT fullname FROM CONSEJERAS WHERE subsidiaryid = '1' ORDER BY fullname ASC"
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
      guerlain_specific = find_specifics(LIST_ID_PA, email_address, "GUERLAIN", request.form.getlist("guerlain-specific"))
      sisley_specific = find_specifics(LIST_ID_PA, email_address, "SISLEY", request.form.getlist("sisley-specific"))
      adp_specific = find_specifics(LIST_ID_PA, email_address, "ADP", request.form.getlist("adp-specific"))
      payot_specific = find_specifics(LIST_ID_PA, email_address, "PAYOT", request.form.getlist("payot-specific"))
      phyto_specific = "" #find_specifics(LIST_ID_PA, email_address, "PHYTO", request.form.getlist("phyto-specific"))
      advisor = request.form["CONSEJERA"]
      notas = request.form["notes"]
      my_geoloc = request.form["geo"]
      # if birth_day == "":
      #   error = "Se requiere fecha de cumpleaños"
      #   flash(error, "alert-danger")
      if not form_interests:
        error = "Se requiere al menos una marca"
        flash(error, "alert-warning")
      else:
        for interest in form_interests:
          interests[interest] = True

        #
        # Add customer data to Mailchimp
        #
        if email_address != "":
          add_customer(LIST_ID_PA, email_address, first_name, last_name,
                      phone, birth_day, gender, store, advisor, country,
                      state, interests, guerlain_specific, sisley_specific,
                      adp_specific, payot_specific, phyto_specific, notas, my_geoloc)


    return render_template("forms/panama.html", my_brands=my_brands, beauty_advisors=beauty_advisors, stores=stores)


@bp.route("/colombia", methods=("GET", "POST"))
def colombia():
    """Transacctional Data for Customers"""
    my_brands = get_brands(LIST_ID_CO, GROUP_ID_CO)
    db = get_db()
    beauty_advisors = db.execute(
        "SELECT fullname FROM CONSEJERAS WHERE subsidiaryid = '2' ORDER BY fullname ASC"
    ).fetchall()
    stores = db.execute(
        "SELECT storename FROM TIENDAS WHERE subsidiaryid = '2' ORDER BY storename ASC"
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
      guerlain_specific = "" #find_specifics(LIST_ID_CO, email_address, "GUERLAIN", request.form.getlist("guerlain-specific"))
      sisley_specific = "" #find_specifics(LIST_ID_CO, email_address, "SYSLEY", request.form.getlist("sisley-specific"))
      adp_specific = find_specifics(LIST_ID_CO, email_address, "ADP", request.form.getlist("adp-specific"))
      payot_specific = find_specifics(LIST_ID_CO, email_address, "PAYOT", request.form.getlist("payot-specific"))
      phyto_specific = find_specifics(LIST_ID_CO, email_address, "PHYTO", request.form.getlist("phyto-specific"))
      advisor = request.form["CONSEJERA"]
      notas = request.form["notes"]
      my_geoloc = None #request.form["geo"]
      # if birth_day == "":
      #   error = "Se requiere fecha de cumpleaños"
      #   flash(error, "alert-danger")
      if not form_interests:
        error = "Se requiere al menos una marca"
        flash(error, "alert-warning")
      else:
        for interest in form_interests:
          interests[interest] = True

        #
        # Add customer data to Mailchimp
        #
        if email_address != "":
          add_customer(LIST_ID_CO, email_address, first_name, last_name,
                      phone, birth_day, gender, store, advisor, country,
                      state, interests, guerlain_specific, sisley_specific,
                      adp_specific, payot_specific, phyto_specific, notas, my_geoloc)



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
                 adp_specific:str, payot_specific:str, phyto_specific:str, notes:str, geoloc:str):
  """This function create a new customer
  in Mailchimp Platform"""
  try:
    client = MailchimpMarketing.Client()
    client.set_config({
      "api_key": API_KEY,
      "server": SERVER_PREFIX
    })
    now = datetime.now()

    # convert email to md5 hash
    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

    # Add or Update a member
    response = client.lists.set_list_member(list_id, subscriber_hash, {
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
    flash("El Usuario fue creado/actualizado éxitosamente", "alert-success")

  except ApiClientError as error:
    error_json = json.loads(error.text)
    log = open("error.log", "+a")
    log.write(f"{now} - {email} - {beauty_advisor}: {json.dumps(error_json)} Geoloc: {geoloc}\n")
    log.close()
    flash(error.text, "alert-danger")
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


def find_specifics(list_id, email, specific, new_options):
  try:
    client = MailchimpMarketing.Client()
    client.set_config({
      "api_key": API_KEY,
      "server": SERVER_PREFIX
    })

    subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
    response = client.lists.get_list_member(list_id, subscriber_hash)

    data_list = str(response["merge_fields"][specific]).split(";")
    data = ";".join(data_list + new_options)
    return re.sub("^;", "", data)


  except ApiClientError as error:
    my_error = json.loads(error.text)
    if my_error["title"] == "Resource Not Found":
      new_specific = ";".join(new_options)
      return re.sub("^;", "", new_specific)
    else:
      print("Error: {}".format(error.text))


def lastday_of_month(mydate:datetime):
  """Find the last day of a month
  Parameters:
    @mydate(datetime)
  Returns: datetime"""
  next_month = mydate.replace(day=28) + timedelta(days=4)
  res = next_month - timedelta(days=next_month.day)
  return res
