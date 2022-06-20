import requests
from datetime import datetime
import smtplib
import time
import os

MY_EMAIL = os.environ["MY_EMAIL"]
MY_PASSWORD = os.environ["MY_PASSWORD"]
MY_LAT = os.environ["MY_LAT"]  # Your latitude
MY_LON = os.environ["MY_LON"]  # Your longitude


def is_iss_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    # Your position is within +5 or -5 degrees of the ISS position.
    if MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and MY_LON - 5 <= iss_longitude <= MY_LON + 5:
        return True


def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LON,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0]) + 8
    if sunrise >= 24:
        sunrise -= 24
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0]) + 8

    time_now = datetime.now().hour

    if time_now >= sunset or time_now <= sunrise:
        return True


while True:
    time.sleep(60)
    if is_night() and is_iss_overhead():
        connection = smtplib.SMTP("smtp.mail.yahoo.com")
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=os.environ["to_addrs"],
                            msg="Subject:Look Up\n\nThe ISS is above you in the sky."
                            )
