from dotenv import load_dotenv
from pathlib import Path
import calendar
import datetime
import sqlite3
import base64
import csv
import sys
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, From, Disposition, Subject, To, HtmlContent)

# load script parameters
working_directory = sys.argv[1]

# load enviroment variables
load_dotenv(Path(f"{working_directory}/.env"))
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# Current Day
current_date = datetime.date.today()


def send_testers(subsidiary: int, emailTo: str):
  """Send an email of the tester request
  Parameters:
    @subsidiary (int): indicate the subsidiary
    @emailTo (str): alias to send email
  Returns: <nothing>
  """
  # Connect to the database
  conn = sqlite3.connect(f'{working_directory}/instance/App.sqlite')
  cursor = conn.cursor()

  # Execute your SQL query
  cursor.execute(
      f"SELECT T1.pos_name, T0.requester, T0.itemcode, T2.tester_name, 1 AS 'Qty', Date(T0.orderdate) AS'orderdate' "
      f"FROM ORDEREDTESTERS T0 "
      f"INNER JOIN POS T1 ON T0.orderpos = T1.id "
      f"INNER JOIN TESTERS T2 ON T0.itemcode = T2.testercode "
      f"WHERE strftime('%m', T0.orderdate) = strftime('%m', 'now') AND T0.Subsidiary = {subsidiary}"
  )
  result = cursor.fetchall()

  # Close the database connection
  conn.close()

  # Define the CSV filename
  csv_filename = f'probadores_al_{current_date}.csv'

  # Export the query result to a CSV file
  with open(csv_filename, 'w', newline='') as csv_file:
      csv_writer = csv.writer(csv_file, delimiter=';')
      csv_writer.writerow([i[0] for i in cursor.description])  # Write column headers
      csv_writer.writerows(result)

  message = Mail(
      from_email=From('no-reply@panabel.com', 'NO-REPLY - GRUPO PANABEL'),
      to_emails=To(f'{emailTo}@panabel.com', "Probadores Panabel"),
      subject=Subject(f'Pedido de probadores al {current_date}'),
      html_content=HtmlContent(f"""
      <div style="font-family: sans-serif;">
          <p>Hola a todos,</p>

          <p>Adjunto encontraran el pedido de probadores de este mes.</p>

          <p>Nombre del archivo adjunto: {csv_filename}</p>

          <p>Saludos,<br>
          Departamento de IT</p>
      </div>
      """)
  )

  with open(f"{csv_filename}", 'rb') as f:
      data = f.read()
      f.close()
  encoded_file = base64.b64encode(data).decode()

  attachedFile = Attachment(
      FileContent(encoded_file),
      FileName(f'{csv_filename}'),
      FileType('text/csv'),
      Disposition('attachment')
  )
  message.attachment = attachedFile

  message_body = message.get()

  sg = SendGridAPIClient(SENDGRID_API_KEY)
  response = sg.send(message_body)
  if response.status_code != 202:
     # en caso de error
     print(f"\nStatus: {response.status_code}\n\nBody:\n{response.body}\n\nHeaders:\n\n{response.headers}\n")

  print("\nEmail enviado exitosamente!\n")
  # Delete File Sent
  if os.path.exists(csv_filename):
    # aling here
    os.remove(csv_filename)
  else:
    print("File not found!")


# Execute email send on the 11
# and the last day of the month
# every month.
if current_date.day == 16:
   send_testers(1,"probadores")
elif current_date == calendar.monthrange(current_date.year, current_date.month)[1]:
   send_testers(2, "probadores.colombia")
else:
   print(f"\nNo email was sent! The day of the month is {current_date.day}\n")
