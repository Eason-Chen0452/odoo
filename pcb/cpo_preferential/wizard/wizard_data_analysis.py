# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class cpo_data_analysis(models.TransientModel):
    _name = 'preferential.data_analysis'
    _description = 'Preferential data analysis'

    cpo_time_bool = fields.Boolean(string='Time analysis')
    cpo_coupon_bool = fields.Boolean(string='Coupon analysis')
    cpo_all_bool = fields.Boolean('All analysis')
    time_money_id = fields.Many2many('preferential.cpo_time_and_money', string='Selected offers')
    cpo_start = fields.Date(string='Search start time')
    cpo_end = fields.Date(string='Search end time')
    cpo_draft_bool = fields.Boolean('Draft status')
    cpo_force_bool = fields.Boolean('Effective yet started status')
    cpo_started_bool = fields.Boolean('Effective and started status')
    cpo_over_bool = fields.Boolean('Invalid and over status')

    @api.onchange('cpo_all_bool')
    def _onchange_all_bool(self):
        if self.cpo_all_bool:
            self.update({'cpo_time_bool': 0, 'cpo_all_bool': 1, 'cpo_coupon_bool': 0})

    @api.onchange('cpo_time_bool')
    def _onchange_time_bool(self):
        if self.cpo_time_bool:
            self.update({'cpo_time_bool': 1, 'cpo_all_bool': 0, 'cpo_coupon_bool': 0})

    @api.onchange('cpo_coupon_bool')
    def _onchange_coupon_bool(self):
        if self.cpo_coupon_bool:
            self.update({'cpo_time_bool': 0, 'cpo_all_bool': 0, 'cpo_coupon_bool': 1})

    @api.onchange('cpo_draft_bool', 'cpo_force_bool', 'cpo_started_bool', 'cpo_over_bool',
                  'cpo_all_bool', 'cpo_time_bool', 'cpo_coupon_bool', 'cpo_start', 'cpo_end')
    def _onchange_all_bool_time(self):
        draft = None
        force = None
        started = None
        over = None
        name_ids = self.time_money_id.search([('cpo_amount_bool', '=?', self.cpo_coupon_bool),
                                              ('cpo_date_bool', '=?', self.cpo_time_bool)]).ids
        if self.cpo_draft_bool:
            draft = 'draft'
        if self.cpo_force_bool:
            force = 'force_no_started'
        if self.cpo_started_bool:
            started = 'started_and_started'
        if self.cpo_over_bool:
            over = 'invalid_over'
        status_ids = self.time_money_id.search([('state', 'in', (draft, force, started, over))]).ids
        date_ids = self.time_money_id.search([('cpo_start_time', '>=', self.cpo_start),
                                              ('cpo_end_time', '<=', self.cpo_end)]).ids
        if not self.cpo_all_bool and not self.cpo_time_bool and not self.cpo_coupon_bool:
            self.update({'time_money_id': [(6, 0, [])]})
        elif self.cpo_coupon_bool or self.cpo_all_bool or self.cpo_time_bool:
            if status_ids and date_ids:
                self.update({'time_money_id': [(6, 0, list(set(name_ids) & set(status_ids) & set(date_ids)))]})
            elif not date_ids and not status_ids:
                self.update({'time_money_id': [(6, 0, name_ids)]})
            elif date_ids and not status_ids:
                self.update({'time_money_id': [(6, 0, list(set(name_ids) & set(date_ids)))]})
            elif status_ids and not date_ids:
                self.update({'time_money_id': [(6, 0, list(set(name_ids) & set(status_ids)))]})

    @api.multi
    def data_analysis(self):
        time_money_ids = self.time_money_id.ids
        if time_money_ids:
            customer_contact = self.env['preferential.cpo_customer_contact']
            customer_contact.time_coupon_date_analysis({"x_ids": time_money_ids})
            view_id = self.env.ref('cpo_preferential.preferential_data_analysis_graph_view').id
            return {
                'name': _('Multi-element data analysis graph'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'graph',
                'res_model': 'preferential.cpo_customer_contact',
                'views': [[view_id, 'graph']],
                'domain': [('id', 'in', time_money_ids)],
            }
        else:
            raise ValidationError(_('Please select those offer data to analyze'))
