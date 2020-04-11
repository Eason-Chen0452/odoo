# -*- coding: utf-8 -*-

import werkzeug, urllib, pprint, logging, json, requests
from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.personal_center.controllers.controllers import ActivateAccount as ClientRegistered

_logger = logging.getLogger(__name__)


class Registered(ClientRegistered):

    @http.route()
    def web_email_verifictaion(self, error=None, *args, **kw):
        client = urllib.unquote(kw.get('token'))
        if client:
            client = client.split('&')
            client = request.env['personal.center'].sudo().browse(int(client[1]))
            if client.word:
                request.env['message.center.line'].sudo().get_new_client_message(client)
        return super(Registered, self).web_email_verifictaion(error=error, *args, **kw)
