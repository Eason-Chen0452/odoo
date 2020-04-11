# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

_logger = logging.getLogger(__name__)

class AuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        if request.params.get('login'):
            kw.update({'redirect': request.session.get('redirect')})
            request.session['redirect'] = ''
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw)


class cpo_electron_WebsiteSale(http.Controller):

    @http.route([
        '/pages/error',
    ], type='http', auth="public", website=True)
    def page_error(self, **post):
        values = {}
        return request.render("website_cpo_sale.pcb_pages_404", values)