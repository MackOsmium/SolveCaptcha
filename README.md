<div align="center">
    <img src="https://raw.githubusercontent.com/MackOsmium/SolveCaptcha/master/images/solvecaptcha.png"/>
    <p>SolveCaptcha is a Async/Sync API wrapper for 2captcha with, planned future support for anti-captcha, for Python 3.6+</p>
</div>

### Features

- [x] Normal Captcha
- [x] Text Captcha
- [x] Recaptcha V2 
- [ ] Recaptcha V3
- [ ] GeeTest
- [ ] RotateCaptcha
- [ ] FunCaptcha
- [ ] KeyCaptcha
- [x] hCaptcha
- [x] Capy
- [ ] TikTok

### Install

```
$ pip install git+git://github.com/MackOsmium/SolveCaptcha
```

or

```
$ git clone https://github.com/mackosmium/solvecaptcha.git
$ cd SolveCaptcha
$ pip install .
```

### Quick Examples for ReCaptcha V2

```python
>>> from solvecaptcha import TwoCaptcha
>>> twocaptcha = TwoCaptcha(API_KEY)
>>> print(twocaptcha)
<TwoCaptcha balance=10.42>
>>> response = twocaptcha.recaptcha_v2(googlekey, pageurl)
>>> # POST response.solution
>>> response.report_good()  # Or response.report_bad()
```

Alternatively, you may not want to wait for the recaptcha solution instantly and instead, use the time it is being solved to do other processing. Then at a later time call `get_solution()` yourself.

Example:

```python
>>> response = twocaptcha.recaptcha_v2(googlekey, pageurl, wait=False)
>>> # Do expensive stuff here
>>> response.get_solution()
>>> # POST response.solution
>>> response.report_good()  # Or response.report_bad()
```

Try it out the async module using `python3 -m asyncio`

Example:

```python
>>> from solvecaptcha import AIOTwoCaptcha
>>> twocaptcha = AIOTwoCaptcha(API_KEY)
>>> response = await twocaptcha.recaptcha_v2(googlekey, pageurl)
```