# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_cpo_sale.controllers.pcb_quotation import ContactusMessage


class InContactusMessage(ContactusMessage):
    """
    继承Contactus 的留言路径
    """

    def _contactus_message_create(self, vals):
        cu_data = request.env['contactus_message.contactus'].sudo().cu_create(vals)
        return cu_data
