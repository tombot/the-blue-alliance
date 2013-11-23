import json
import logging
import webapp2

from controllers.base_controller import CacheableHandler
from helpers.validation_helper import ValidationHelper

class ApiBaseController(CacheableHandler):

    def __init__(self, *args, **kw):
        super(ApiBaseController, self).__init__(*args, **kw)
        self.response.headers['content-type'] = 'application/json; charset="utf-8"'

    def handle_exception(self, exception, debug):
        """
        Handle an HTTP exception and actually writeout a 
        response.
        Called by webapp when abort() is called, stops code excution.
        """
        logging.info(exception)
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
            self.response.out.write(self._errors)
        else:
            self.response.set_status(500)

    def get(self, *args, **kw):
        self._validate_user_agent()
        self._errors = ValidationHelper.validate(self._validators)
        if self._errors:
            self.abort(400)

        super(ApiBaseController, self).get(*args, **kw)

    def _validate_user_agent(self):
        """
        Tests the presence of a User-Agent header.
        """
        if self.request.headers.get("User-Agent") is None:
            self._errors = json.dumps({"Error": "User-Agent is a required header."})
            self.abort(400)

    def _write_cache_headers(self, seconds):
        if type(seconds) is not int:
            logging.error("Cache-Control max-age is not integer: {}".format(seconds))
            return

        self.response.headers['Cache-Control'] = "public, max-age=%d" % seconds
        self.response.headers['Pragma'] = 'Public'