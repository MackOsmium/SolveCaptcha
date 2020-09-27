class SolveCaptchaError(BaseException):
    """Base class for all Errors"""
    pass

class CaptchaTimeoutError(SolveCaptchaError):
    """Timed out while waiting for captcha solution"""
    pass

class TwoCaptchaInputError(SolveCaptchaError):
    pass

class TwoCaptchaResponseError(SolveCaptchaError):
    pass
