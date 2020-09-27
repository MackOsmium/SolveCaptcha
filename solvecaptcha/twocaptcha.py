"""twocaptcha.py - Synchronous Module for interacting
wit the 2Captcha API.
"""
import time
import json
from requests.api import get, post

import solvecaptcha.errors as errors


# Typing
ApiKey = str
Base64Str = str

# Constants
BASE = "https://2captcha.com"
SOFT_ID = "2621"


class TwoCaptchaBase:
    key = None

    def _in(self, method: str = None, **kwargs):
        params = {"key": self.key, "method": method, "soft_id": SOFT_ID}
        if not method:
            params.pop("method")

        if kwargs:
            params = {**params, **kwargs}

        with post(f"{BASE}/in.php", data=params) as r:
            if "ERROR" in r.text:
                raise errors.TwoCaptchaInputError(r.text)
            return r.text.replace("OK|", "")

    def _res(self, action: str, **kwargs):
        params = {"key": self.key, "action": action}
        if kwargs:
            params = {**params, **kwargs}

        with get(f"{BASE}/res.php", params=params) as r:
            if "ERROR" in r.text:
                raise errors.TwoCaptchaResponseError(r.text)
            return r.text.replace("OK|", "")


class TwoCaptchaResponse(TwoCaptchaBase):
    __slots__ = ("key", "request_id", "solution")

    def __init__(self, key: ApiKey, request_id: str, solution: str = None):
        super().__init__()

        self.key = key
        self.request_id = request_id
        self.solution = solution

    def report_good(self):
        self._res("reportgood", id=self.request_id)

    def report_bad(self):
        self._res("reportbad", id=self.request_id)

    def __repr__(self):
        return self.solution


class TwoCaptcha(TwoCaptchaBase):
    __slots__ = ("key", "timeout")

    def __init__(self, key: ApiKey, timeout: int = 300):
        """[summary]

        Parameters
        ----------
        key : ApiKey
            2Captcha api key
        timeout : int, optional
            Timeout for recieving Captcha solution, by default 300
        """
        super().__init__()

        self.key = key
        self.timeout = timeout

    def get_solution(self, id: int) -> TwoCaptchaResponse:
        for _ in range(self.timeout // 5):
            r = self._res("get", id=id)
            if "CAPCHA_NOT_READY" in r:
                time.sleep(5)
                continue
            return r

        raise errors.CaptchaTimeoutError("Did not recieve captcha solution in set time")

    def captcha(self, encoded_string: Base64Str, textinstructions: str, **kwargs) -> TwoCaptchaResponse:
        """Solve a regular captcha

        Parameters
        ----------
        encoded_string : Base64Str
            Base64 encoded Captcha image
        textinstructions : str
            Text instructions to be given to the worker

        Attributes
        ----------
        phrase : int
            Specifies if the captcha contain two or more words
                0 - One word
                1 - Two or more words
        regsense : int
            Specifies if the captcha case sensitive
                0 - captcha in not case sensitive
                1 - captcha is case sensitive
        numeric : int
            Specifies what characters the captcha contains
                0 - not specified
                1 - captcha contains only numbers
                2 - captcha contains only letters
                3 - captcha contains only numbers OR only letters
                4 - captcha contains both numbers AND letters
        Full list of Attributes:
            https://2captcha.com/2captcha-api#solving_normal_captcha
        Returns
        -------
        TwoCaptchaResponse
        """
        id = self._in("base64", body=encoded_string, textinstructions=textinstructions, **kwargs)

        time.sleep(5)

        solution = self.get_solution(id)
        response = TwoCaptchaResponse(self.key, id, solution)
        return response

    def textcaptcha(self, text: str, lang: str = "en", language: int = 0, **kwargs) -> TwoCaptchaResponse:
        """Solve a Text Captcha.

        https://2captcha.com/2captcha-api#solving_text_captcha
        > Text Captcha is a type of captcha that is represented as text and doesn't contain images.
        > Usually you have to answer a question to pass the verification.

        Parameters
        ----------
        text : str
            The text captchas contents, e.g. "What day is today?"
        lang : str, optional
            Language code, availabe language codes: 2captcha.com/2captcha-api#language, by default "en"
        language : int, optional
            Alphabet in use, 0 - not specified,
                             1 - Cyrillic (Russian) captcha,
                             2 - Latin captchai
            by default 0
        time_limit : int, optional
            Time limit until response is recieved, in seconds, by default 300

        Returns
        -------
        TwoCaptchaResponse
        """
        id = self._in(textcaptcha=text, language=language, **kwargs)

        time.sleep(5)

        solution = self.get_solution(id)
        response = TwoCaptchaResponse(self.key, id, solution)
        return response

    def recaptcha_v2(self, googlekey: str, pageurl: str, **kwargs) -> TwoCaptchaResponse:
        """Solve ReCaptcha V2
        Parameters
        ----------
        googlekey : [type]
            Value of k or data-sitekey parameter, example: 6LfP0CITAAAAAHq9FOgCo7v_fb0-pmmH9VW3ziFs
        pageurl : [type]
            Full URL of the page where the ReCaptcha is present
        time_limit : int, optional
            Time limit until response is recieved, in seconds, by default 300

        Returns
        -------
        TwoCaptchaResponse
        """
        id = self._in("userrecaptcha", googlekey=googlekey, pageurl=pageurl, **kwargs)

        time.sleep(20)

        solution = self.get_solution(id)
        response = TwoCaptchaResponse(self.key, id, solution)
        return response

    def hcaptcha(self, sitekey: str, pageurl: str, **kwargs) -> TwoCaptchaResponse:
        id = self._in("hcaptcha", sitekey=sitekey, pageurl=pageurl, **kwargs)

        time.sleep(20)

        solution = self.get_solution(id)
        response = TwoCaptchaResponse(self.key, id, solution)
        return response

    def capy(self, captchakey: str, pageurl: str, apiserver: str, **kwargs) -> TwoCaptchaResponse:
        id = self._in("capy", captchakey=captchakey, pageurl=pageurl, apiserver=apiserver, **kwargs)

        time.sleep(20)

        solution = json.loads(self.get_solution(id))
        response = TwoCaptchaResponse(self.key, id, solution)
        return response

    def _get_balance(self) -> float:
        r = self._res("getbalance")
        return float(r)

    @property
    def balance(self) -> float:
        return self._get_balance()

    def __repr__(self):
        return f"<TwoCaptcha balance={self.balance}>"
