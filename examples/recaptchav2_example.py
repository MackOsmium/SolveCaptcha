"""recaptchav2_example.py - Solving the example
recaptcha on www.google.com/recaptcha/api2/demo
using python requests.
"""
import requests
import os
from solvecaptcha import TwoCaptcha


API_KEY = os.environ.get("API_KEY")
URL = "https://www.google.com/recaptcha/api2/demo"


twocaptcha = TwoCaptcha(API_KEY)
response = twocaptcha.recaptcha_v2("6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-", URL)

with requests.post(URL, data={"g-recaptcha-response": response.solution}) as r:
    if "Verification Success... Hooray!" in r.text:
        print("Successfully solved the captcha!")
        response.report_good()
    else:
        print("Solving Captcha failed :(")
        response.report_bad()
