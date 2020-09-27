import base64
import os
from solvecaptcha import TwoCaptcha


API_KEY = os.environ.get("API_KEY")


with open("./example_data/normal_captcha.jpg", "rb") as f:
    b64_str = base64.b64encode(f.read()).decode()

twocaptcha = TwoCaptcha(API_KEY)

# If case sensitive regsense=1
response = twocaptcha.captcha(b64_str, "Only text", regsense=0)
if response.solution.lower() == "bjnf":
    print("Got correct response!")
    response.report_good()
else:
    print("Got incorrect response :(")
    response.report_bad()
