import asyncio
from aiohttp import ClientSession

import solvecaptcha.errors as errors

# Typing
ApiKey = str
Base64Str = str

# Constants
BASE = "https://2captcha.com"
SOFT_ID = "2621"


# Simple GET/POST wrappers for aiohttp
async def get(url, **kwargs) -> str:
    async with ClientSession() as session:
        r = await session.get(url, **kwargs)
        return await r.text()

async def post(url, **kwargs) -> str:
    async with ClientSession() as session:
        r = await session.post(url, **kwargs)
        return await r.text()


class AIOTwoCaptchaBase:
    key = None

    async def _in(self, method: str = None, **kwargs):
        params = {"key": self.key, "method": method, "soft_id": SOFT_ID}
        if not method:
            params.pop("method")

        if kwargs:
            params = {**params, **kwargs}

        r = await post(f"{BASE}/in.php", data=params)
        if "ERROR" in r:
            raise errors.TwoCaptchaInputError(r)
        return r.replace("OK|", "")

    async def _res(self, action: str, **kwargs):
        params = {"key": self.key, "action": action}
        if kwargs:
            params = {**params, **kwargs}

        r = await get(f"{BASE}/res.php", params=params)
        if "ERROR" in r:
            raise errors.TwoCaptchaResponseError(r)
        return r.replace("OK|", "")


class AIOTwoCaptchaResponse(AIOTwoCaptchaBase):
    __slots__ = ("key", "request_id", "timeout", "solution")
    def __init__(self, key: ApiKey, request_id: str, timeout: int = 300):
        super().__init__()

        self.key = key
        self.request_id = request_id
        self.timeout = timeout

        self.solution = None

    async def get_solution(self):
        for _ in range(self.timeout // 5):
            r = await self._res("get", id=self.request_id)
            if "CAPCHA_NOT_READY" in r:
                await asyncio.sleep(5)
                continue
            self.solution = r
            return self

        raise errors.CaptchaTimeoutError("Did not recieve captcha solution in set time")

    async def report_good(self):
        await self._res("reportgood", id=self.request_id)

    async def report_bad(self):
        await self._res("reportbad", id=self.request_id)

    def __repr__(self):
        return self.solution


class AIOTwoCaptcha(AIOTwoCaptchaBase):
    __slots__ = ("key", "timeout")

    def __init__(self, key: ApiKey, timeout: int = 300):
        """
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

    def captcha(self, encoded_string: Base64Str, textinstructions: str, wait: bool = True, **kwargs) -> AIOTwoCaptchaResponse:
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
        id = await self._in("base64", body=encoded_string, textinstructions=textinstructions, **kwargs)

        response = AIOTwoCaptchaResponse(self.key, id, self.timeout)

        if wait:
            await asyncio.sleep(5)
            return await response.get_solution()

        return response

    def textcaptcha(self, text: str, lang: str = "en", language: int = 0, wait: bool = True, **kwargs) -> AIOTwoCaptchaResponse:
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
        id = await self._in(textcaptcha=text, language=language, **kwargs)

        response = AIOTwoCaptchaResponse(self.key, id, self.timeout)

        if wait:
            await asyncio.sleep(5)
            return await response.get_solution()

        return response

    async def recaptcha_v2(self, googlekey: str, pageurl: str, wait: bool = True, **kwargs) -> AIOTwoCaptchaResponse:
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
        TwoCaptchaRespons
        """
        id = await self._in("userrecaptcha", googlekey=googlekey, pageurl=pageurl, **kwargs)

        response = AIOTwoCaptchaResponse(self.key, id, self.timeout)

        if wait:
            await asyncio.sleep(20)
            return await response.get_solution()

        return response

    def hcaptcha(self, sitekey: str, pageurl: str, wait: bool = True, **kwargs) -> AIOTwoCaptchaResponse:
        id = await self._in("hcaptcha", sitekey=sitekey, pageurl=pageurl, **kwargs)

        response = AIOTwoCaptchaResponse(self.key, id, self.timeout)

        if wait:
            await asyncio.sleep(20)
            return await response.get_solution()

        return response

    def capy(self, captchakey: str, pageurl: str, apiserver: str, wait: bool = True, **kwargs) -> AIOTwoCaptchaResponse:
        id = await self._in("capy", captchakey=captchakey, pageurl=pageurl, apiserver=apiserver, **kwargs)

        response = AIOTwoCaptchaResponse(self.key, id, self.timeout)

        if wait:
            await asyncio.sleep(20)
            return await response.get_solution()

        return response
