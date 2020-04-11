# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.addons.personal_center.models.models import PersonalCenter


class ClientDataShow(models.Model):
    _inherit = 'personal.center'

    @api.multi
    # 前端调用客户个人订单接口
    def get_partner(self, partner_id, value):
        return self.GetPartnerOrder(partner_id, value)

    def GetPartnerOrder(self, partner_id, value):
        # orders = partner_id.with_context({'tz': partner_id.tz, 'lang': partner_id.lang}).sale_order_ids
        orders = partner_id.sale_order_ids
        contact = self.env['preferential.cpo_customer_contact'].search([('partner_id', '=', partner_id.id),
                                                                        ('cpo_use_bool', '=', False),
                                                                        ('cpo_invalid_bool', '=', False)])
        ask = self.env['ask.guest'].search([('partner_id', '=', partner_id.id), ('state', 'in', ['wait_reply', 's_append'])])
        x_dict = {
            'qty': {
                'ur_qty': len(orders.filtered(lambda x: x.state in ['wait_confirm', 'sent', 'sale'])),
                'py_qty': len(orders.filtered(lambda x: x.state == 'wait_payment')),
                'm_qty': len(orders.filtered(lambda x: x.state in ['wait_make', 'manufacturing'])),
                'd_qty': len(orders.filtered(lambda x: x.state in ['wait_delivery', 'wait_receipt'])),
                'c_qty': len(orders.filtered(lambda x: x.state == 'complete')),
                'cp_qty': len(contact),
                'ask_qty': len(ask),
            }
        }
        if value == 'under_review':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_confirm', 'sent', 'sale'])})
        elif value == 'manufacturing':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_make', 'manufacturing'])})
        elif value == 'delivery':
            x_dict.update({'order': orders.filtered(lambda x: x.state in ['wait_delivery', 'wait_receipt'])})
        elif value == 'completed':
            x_dict.update({'order': orders.filtered(lambda x: x.state == 'complete')})
        elif value == 'awaiting_payment':
            x_dict.update({
                'invoice_qty': self.env['account.invoice'].sudo().search([
                    ('type', 'in', ['out_invoice', 'out_refund']),
                    ('state', 'in', ['open', 'paid', 'cancel']),
                    ('message_partner_ids', 'child_of', partner_id.commercial_partner_id.ids)
                ])
            })
        return x_dict
