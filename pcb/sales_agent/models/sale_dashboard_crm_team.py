# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmTeamSalesAgent(models.Model):
    _inherit = 'crm.team'

    count_complex_1 = fields.Char('Complex Count', compute='_compute_dashboard_button_name')
    count_complex_2 = fields.Char('Complex Count', compute='_compute_dashboard_button_name')
    count_complex_3 = fields.Char('Complex Count', compute='_compute_dashboard_button_name')
    count_complex_4 = fields.Char('Complex Count', compute='_compute_dashboard_button_name')
    count_complex_5 = fields.Char('Complex Count', compute='_compute_dashboard_button_name')

    def _compute_dashboard_button_name(self):
        sale = self.env['sale.order']
        now = fields.datetime.now().strftime('%Y-%m-%d')
        sale = {
            'D': sale.search([('state', 'in', ('draft', 'cancel'))]).ids,
            'H': sale.search([('state', 'not in', ('draft', 'done', 'cancel', 'complete'))]).ids,
            'C': sale.search([('state', '=', 'complete')]).ids,
            'pcb': sale.search([('product_type', 'not in', ('PCBA', 'Stencil'))]).ids,
            'pcba': sale.search([('product_type', '=', 'PCBA')]).ids,
            'stencil': sale.search([('product_type', '=', 'Stencil')]).ids
        }
        web = {
            'n_pcb': self.env['cpo_pcb_record'].search([('cpo_time', '>=', now), ('cpo_time', '<=', now)]).ids,
            'n_pcba': self.env['cpo_pcba_record'].search([('cpo_time', '>=', now), ('cpo_time', '<=', now)]).ids,
            'n_all': self.env['cpo_pcb_and_pcba_record'].search([('cpo_time', '>=', now), ('cpo_time', '<=', now)]).ids,
            'pcb': self.env['cpo_pcb_record'].search([('cpo_time', '<', now)]).ids,
            'pcba': self.env['cpo_pcba_record'].search([('cpo_time', '<', now)]).ids,
            'all': self.env['cpo_pcb_and_pcba_record'].search([('cpo_time', '<', now)]).ids,
        }
        order = self.filtered(lambda x: x.team_type == 'sales')
        order.update({
            'dashboard_button_name': _("Order Inquiry (Do Not Have To Deal With)") + ' - ' + str(len(sale.get('D'))),
            'count_complex_1': _('Order Waiting Processing') + ' - ' + str(len(sale.get('H'))),
            'count_complex_2': _('Order Completed') + ' - ' + str(len(sale.get('C'))),
            'count_complex_3': _('PCB Order') + ' - ' + str(len(sale.get('pcb'))),
            'count_complex_4': _('PCBA Order') + ' - ' + str(len(sale.get('pcba'))),
            'count_complex_5': _('Stencil Order') + ' - ' + str(len(sale.get('stencil'))),
        })
        (self - order).update({
            'dashboard_button_name': _("PCB ToDay Trial Price") + ' - ' + str(len(web.get('n_pcb'))),
            'count_complex_1': _('PCBA ToDay Trial Price') + ' - ' + str(len(web.get('n_pcba'))),
            'count_complex_2': _('PCB & PCBA ToDay Trial Price') + ' - ' + str(len(web.get('n_all'))),
            'count_complex_3': _('PCB Historical Trial Price') + ' - ' + str(len(web.get('pcb'))),
            'count_complex_4': _('PCBA Historical Trial Price') + ' - ' + str(len(web.get('pcba'))),
            'count_complex_5': _('PCB & PCBA Historical Trial Price') + ' - ' + str(len(web.get('all'))),
        })

    def action_primary_channel_button(self):
        if hasattr(self, 'use_opportunities') and self.use_opportunities:
            return super(CrmTeamSalesAgent, self).action_primary_channel_button()
        value = self._context.get('value')
        if self.team_type == 'sales':
            action = self.env.ref('sale_pcb_rfq.rfq_sale_order_quotations').read()[0]
            if value == '1':
                action['domain'] = [('state', 'in', ('draft', 'cancel'))]
                action['display_name'] = _('Order Inquiry (Do Not Have To Deal With)')
            elif value == '2':
                action['domain'] = [('state', 'not in', ('draft', 'done', 'cancel', 'complete'))]
                action['display_name'] = _('Order Waiting Processing')
            elif value == '3':
                action['domain'] = [('state', '=', 'complete')]
                action['display_name'] = _('Order Completed')
            elif value == '4':
                action['domain'] = [('product_type', 'not in', ('PCBA', 'Stencil'))]
                action['display_name'] = _('PCB Order')
            elif value == '5':
                action['domain'] = [('product_type', '=', 'PCBA')]
                action['display_name'] = _('PCBA Order')
            elif value == '6':
                action['domain'] = [('product_type', '=', 'Stencil')]
                action['display_name'] = _('Stencil Order')
            return action
        else:
            now = fields.datetime.now().strftime('%Y-%m-%d')
            value_list = [('cpo_time', '>=', now), ('cpo_time', '<=', now)]
            value_list_1 = [('cpo_time', '<', now)]
            action = None
            if value == '1':
                action = self.env.ref('website_cpo_index.cpo_pcb_record_all_pcb_actions').read()[0]
                action['domain'] = value_list
                action['display_name'] = _('PCB ToDay Trial Price')
            elif value == '2':
                action = self.env.ref('website_cpo_index.cpo_pcb_record_all_pcba_actions').read()[0]
                action['domain'] = value_list
                action['display_name'] = _('PCBA ToDay Trial Price')
            elif value == '3':
                action = self.env.ref('website_cpo_index.cpo_pcb_and_pcba_record_actions').read()[0]
                action['domain'] = value_list
                action['display_name'] = _('PCB & PCBA ToDay Trial Price')
            elif value == '4':
                action = self.env.ref('website_cpo_index.cpo_pcb_record_all_pcb_actions').read()[0]
                action['domain'] = value_list_1
                action['display_name'] = _('PCB Historical Trial Price')
            elif value == '5':
                action = self.env.ref('website_cpo_index.cpo_pcb_record_all_pcba_actions').read()[0]
                action['domain'] = value_list_1
                action['display_name'] = _('PCBA Historical Trial Price')
            elif value == '6':
                action = self.env.ref('website_cpo_index.cpo_pcb_and_pcba_record_actions').read()[0]
                action['domain'] = value_list_1
                action['display_name'] = _('PCB & PCBA Historical Trial Price')
            return action



