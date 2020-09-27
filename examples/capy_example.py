import requests
import os
from solvecaptcha import TwoCaptcha


API_KEY = os.environ.get("API_KEY")
URL = "https://www.capy.me/products/puzzle_captcha/"


twocaptcha = TwoCaptcha(API_KEY)
response = twocaptcha.capy("PUZZLE_h4k2THJgd5dR5jYrKRHdddaSEp7aDN",
                           "https://www.capy.me/products/puzzle_captcha/",
                           "https://www.capy.me")

requests.post(URL, data=response.solution)
