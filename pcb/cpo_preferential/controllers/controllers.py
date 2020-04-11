# -*- coding: utf-8 -*-

import json, werkzeug, logging
from odoo import http
from odoo.http import request

_logging = logging.getLogger(__name__)


class JsonSalePreferential(http.Controller):

    # Sale Preferential
    @http.route(['/api/get_coupon'], type='json', auth='public', website=True)
    def get_coupon(self, **kw):
        try:
            sale_coupon = request.env['preferential.cpo_customer_contact'].sudo().get_public_mark_coupon(kw)
            return json.dumps(sale_coupon)
        except Exception as e:
            _logging.exception("An exception occured during an http request")
            error = {
                'code': 400,
                'message': "Odoo Server Error",
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))