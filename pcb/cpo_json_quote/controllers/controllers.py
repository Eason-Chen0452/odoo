# -*- coding: utf-8 -*-
import json, werkzeug, logging
from odoo import http
from odoo.http import request

_logging = logging.getLogger(__name__)


class JsonSaleQuote(http.Controller):

    # PCB Quoted Price
    @http.route(['/api/get_quote/pcb'], type='json', auth='public', website=True, cors="*", csrf=False, method=["GET", "POST"])
    def get_quoted_price_pcb(self, **kw):
        try:
            pcb_quoted = request.env['sale.quotation'].sudo().get_pcb_quotation_price(kw)
            return json.dumps(pcb_quoted)
        except Exception as e:
            _logging.exception("An exception occured during an http request")
            error = {
                'code': 500,
                'message': "Odoo Server Error",
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))

    # PCBA Quoted Price
    @http.route(['/api/get_quote/pcba'], type='json', auth='public', website=True, cors="*", csrf=False, method=["GET", "POST"])
    def get_quoted_price_pcbA(self, **kw):
        try:
            pcbA_quoted = request.env['cpo_smt_price.smt'].sudo().pbca_and_pcb_price_integration(kw)
            return json.dumps(pcbA_quoted)
        except Exception as e:
            _logging.exception("An exception occured during an http request")
            error = {
                'code': 500,
                'message': "Odoo Server Error",
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))

    # PCB Package Price
    @http.route(['/api/package_quote/pcb'], type='json', auth='public', website=True, cors="*", csrf=False, method=["GET", "POST"])
    def get_package_pcb(self, **kw):
        try:
            pcb_quoted = request.env['sale.quotation'].sudo().get_pcb_package(kw)
            pcb_quoted = {'Total Cost': pcb_quoted.get('value').get('Total Cost')}
            return json.dumps(pcb_quoted)
        except Exception as e:
            _logging.exception("An exception occured during an http request")
            error = {
                'code': 500,
                'message': "Odoo Server Error",
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))

    # SMT Package Price
    @http.route(['/api/package_quote/pcba'], type='json', auth='public', website=True, cors="*", csrf=False, method=["GET", "POST"])
    def get_packge_pcba(self, **kw):
        try:
            pcba_quoted = request.env['sale.order'].sudo().get_smt_package(kw)
            return json.dumps(pcba_quoted)
        except Exception as e:
            _logging.exception("An exception occured during an http request")
            error = {
                'code': 500,
                'message': "Odoo Server Error",
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))

