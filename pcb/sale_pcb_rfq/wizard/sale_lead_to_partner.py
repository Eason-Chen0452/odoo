# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re
from odoo.osv import osv
from odoo import api, fields, models, _, tools


class sale_lead_to_partner(osv.osv_memory):
    _name = 'sale.lead.to.partner'
    _description = 'Lead order To sale Order'

    action = fields.Selection([
            ('exist', 'Link to an existing customer'),
            ('create', 'Create a new customer'),
            #('nothing', 'Do not link to a customer')
            ], 'Related Customer', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer')
    confirm_line = fields.One2many('pcblead.to.partner.line', 'confirm_id', 'Quotation Lines')

    def onchange_action(self, action):
        #return {'value': {'partner_id': False if action != 'exist' else self._find_matching_partner(cr, uid, context=context)}}
        vals={'partner_id': False,
              'action': action}
        return {'value': vals}

    def default_get(self, fields):
        """
        Default get for name, opportunity_ids.
        If there is an exisitng partner link to the lead, find all existing
        opportunities links with this partner to merge all information together
        """
        lead_obj = self.pool.get('crm.lead')
        res = super(sale_lead_to_partner, self).default_get(fields)
        quo_obj = self.pool.get('sale.quotation')
        res_id = self.env.context.get('active_id')
        quo_res = quo_obj.browse(res_id)
        if not quo_res.quotation_line:
            raise osv.except_osv(_('Quotation Line Error!'), _('Please enter at least one line of Quotation Line!'))
        value = []
        for row in quo_res.quotation_line:
            value.append((0,0,{'product_no':row.product_no,'customer_file_name':row.customer_file_name}))
        res.update({'confirm_line' : value})
        return res

    def view_init(self, fields):
        """
        Check some preconditions before the wizard executes.
        """
        lead_obj = self.pool.get('sale.quotation')
        for lead in lead_obj.browse(self.env.context.get('active_ids', [])):
            if lead.state in ['done', 'cancel']:
                raise osv.except_osv(_("Warning!"), _("Closed/Cancelled leads cannot be converted into opportunities."))
        return False

    def _convert_sale_order(self, vals):
        lead = self.pool.get('crm.lead')
        res = False
        partner_ids_map = self._create_partner(self)
        lead_ids = vals.get('lead_ids', [])
        team_id = vals.get('section_id', False)
        for lead_id in lead_ids:
            partner_id = partner_ids_map.get(lead_id, False)
            # FIXME: cannot pass user_ids as the salesman allocation only works in batch
            res = lead.convert_opportunity([lead_id], partner_id, [], team_id)
        # FIXME: must perform salesman allocation in batch separately here
        user_ids = vals.get('user_ids', False)
        if user_ids:
            lead.allocate_salesman(lead_ids, user_ids, team_id=team_id)
        return res

    def action_apply(self):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        quo = self.pool.get('sale.quotation')
        check = self.pool.get('cam.engineering.check')
        quo_line_pool = self.pool.get('sale.quotation.line')

        w = self.browse(self.ids)[0]
        lead_ids = self.env.context.get('active_ids', [])
        lead_id = self.env.context.get('active_id')
        row_lead_id = quo.browse(lead_id).lead_id.id
        
        self._convert_sale_order({'lead_ids': [row_lead_id]})
        
        data = quo.browse(lead_id)
        partner = data.lead_id.partner_id and data.lead_id.partner_id.id
        #partner = w.partner_id and w.partner_id.id
        quo.write(lead_id, {'partner_id':partner,'partner_invoice_id':partner,'partner_shipping_id':partner})
        for row in data.quotation_line:
            check.write(row.cam_check.id, {'partner_id':partner})
        for row in w.confirm_line:
            quo_l_rows = quo_line_pool.search([('quotation_id','=',lead_id),('customer_file_name','=',row.customer_file_name)])
            if len(quo_l_rows) >1:
                raise osv.except_osv(_('Customer File Name Error!'), _('Find the same file name!'))
            #quo_l_rows = quo_line_pool.browse(cr, uid, quo_l_rows, context=context)            
            quo_line_pool.write(quo_l_rows[0], {'product_no':row.product_no})
            q_row = quo_line_pool.browse(quo_l_rows[0])
            self.pool.get('cam.engineering.check').write(q_row.cam_check.id, {'product_no':row.product_no})
        quo.onchange_partner_id(lead_ids, partner)
        
        #return self.pool.get('sale.quotation').redirect_quotation_view(cr, uid, lead_ids[0], context=context)
        return self.pool.get('sale.quotation').action_done(lead_ids)

    def _create_partner(self):
        """
        Create partner based on action.
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by crm_lead2opportunity_partner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        lead = self.pool.get('crm.lead')
        lead_ids = self.env.context.get('active_ids', [])
        quotation_pool = self.pool.get('sale.quotation')
        quo_data = quotation_pool.browse(lead_ids)[0]
        data = self.browse(self.ids)[0]
        partner_id = data.partner_id and data.partner_id.id or False
        return lead.handle_partner_assignation([quo_data.lead_id.id], data.action, partner_id)


class pcblead_to_partner_line(osv.osv_memory):
    _name='pcblead.to.partner.line'
    _description="Pcblead To Partner Line"

    confirm_id = fields.Many2one('sale.lead.to.partner', 'Confirm Reference', required=True, ondelete='cascade', index=True)
    product_no = fields.Char('Product No', size=100, required=False)
    customer_file_name = fields.Char('Customer File Name', size=100, required=True)
