# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xlrd, base64, time
from odoo.addons.cpo_offer_base.models.cpo_offer_bom import recheck_bom_file_content

UPDATE_BOM_STATE = [('draft', 'Draft'), ('check', 'Checking'), ('complete', 'Complete')]
UPDATE_BOM_HEAD = [('cpo_item', 'Item - item'),
                   ('cpo_qty', 'Quantity - qty'),
                   ('cpo_p_n', 'P/N - p/n'),
                   ('cpo_description', 'Bom Description - Description'),
                   ('cpo_vendor_p_n', 'Vendor P/N - Vendor'),
                   ('cpo_mfr', 'Manufacturer - Mfr'),
                   ('cpo_mfr_p_n', 'Manufacturer P/N - Mfr p/n'),
                   ('cpo_remark', 'Remark'),
                   ('cpo_package', 'Packaging')]


class inherit_cpo_offer_bom_bom(models.Model):
    _name = 'cpo_offer_bom.bom'
    _inherit = 'cpo_offer_bom.bom'
    # 三个索引字段
    state = fields.Selection(UPDATE_BOM_STATE, default='draft', string="Status")
    cpo_colour = fields.Selection([('no', 'NO'), ('ok', 'OK'), ('YES', 'YES')], string='Order submission', compute='_depends_cpo_colour', store=True)
    cpo_check_bom = fields.Selection([('ok_check', 'OK Check'),
                                      ('no_check', 'NO Check'),
                                      ('checked', 'Checked')], compute='_depends_cpo_check_bom', store=True)
    cpo_table_bom = fields.Boolean(compute='_depends_cpo_colour', store=True)

    @api.one
    @api.depends('state')
    def _depends_cpo_colour(self):
        if not self.order_ids:
            self.cpo_colour, self.cpo_table_bom = 'YES', False
        elif self.order_ids.order_id.state != 'draft':
            self.cpo_colour, self.cpo_table_bom = 'ok', True
        else:
            self.cpo_colour, self.cpo_table_bom = 'no', False

    # 更加cpo_colour状态映射分类
    @api.one
    @api.depends('cpo_colour', 'cpo_table_bom')
    def _depends_cpo_check_bom(self):
        colour, state = self.cpo_colour, self.state
        if colour in ['ok', 'YES'] and state != 'complete':
            self.cpo_check_bom = 'ok_check'
        elif state == 'complete':
            self.cpo_check_bom = 'checked'
        else:
            self.cpo_check_bom = 'no_check'


class inherit_cpo_offer_bom_bom_line(models.Model):
    _name = 'cpo_offer_bom.bom_line'
    _inherit = 'cpo_offer_bom.bom_line'
    # 两个索引字段
    state = fields.Selection(UPDATE_BOM_STATE, related="base_table_bom_id.state", store=False, default='draft')
    cpo_colour = fields.Selection([('no', 'NO'), ('ok', 'OK'), ('YES', 'YES')], related="base_table_bom_id.cpo_colour", default='no', store=False)
    cny_price = fields.Float(digits=(16, 2), string='CNY Price')

    def matched_data(self):
        a = time.time()
        cur = self.env['res.currency'].browse(self.env.ref('base.USD').id)  # 增加
        rate = 6.6 if not cur.rate_ids else cur.rate_ids[0].rate  # 增加
        bom_line = self.filtered(lambda line: line.bom_supply != 'customer')  # 非客供
        for x_line in bom_line:
            (mfr, qty, x_dict) = (x_line.cpo_mfr_p_n, x_line.require_qty, {})
            template = self.env['product.template'].search([('name', '=', mfr)])
            if mfr:  # cpo.product.level.price 对象以 cpo_min_number 大小排序
                prices = template.level_price_line.filtered(lambda line: qty >= line.cpo_min_number)
                if len(prices) >= 1:
                    x_dict.update({'price': prices[0].cpo_price})
                elif not prices:
                    x_dict.update({'price': template.list_price})
                mfr_dict = self.env['electron.disk_center'].get_product_price(mfr)
                if not x_dict.get('price') or x_dict.get('price') <= 0:
                    x_dict.update({'price': mfr_dict.get('price')})
                if mfr_dict.get('package'):
                    x_dict.update({'cpo_package': mfr_dict.get('package')})
                price = x_dict.get('price') if x_dict.get('price') else 0  # 一定保证price 不能为None
                x_dict.update({'cny_price': price * rate, 'total': price * x_line.cpo_qty, 'check_state': 'true1', 'price': price})
                if not mfr_dict:
                    x_dict.update({'check_state': 'flase0'})
                x_line.write(x_dict)
            else:
                x_line.write({'check_state': 'lack'})
        print(time.time()-a)
        return True

    @api.onchange('cny_price')
    def _onchange_check_cny_price(self):
        cur = self.env['res.currency'].browse(self.env.ref('base.USD').id)
        rate = 6.6 if not cur.rate_ids else cur.rate_ids[0].rate
        if self.cny_price > 0:
            return self.update({'price': self.cny_price / rate})


class inherit_cpo_bom_fields_line_for_bom(models.Model):
    _name = 'cpo_bom_fields.line_for_bom'
    _inherit = 'cpo_bom_fields.line_for_bom'
    # 两个索引字段
    cpo_title = fields.Selection(UPDATE_BOM_HEAD, string="CPO Title", required=False)


class inherit_cpo_bom_table_head(models.TransientModel):
    _name = 'cpo_bom_table_head.head'
    _inherit = 'cpo_bom_table_head.head'
    # 一个索引的字段
    cpo_title = fields.Selection(UPDATE_BOM_HEAD, string="Headline")


class inherit_cpo_bom_wizard(models.TransientModel):
    _name = 'cpo_bom_wizard.wizard'
    _inherit = 'cpo_bom_wizard.wizard'

    # 获取上传文件的表头 - 函数修改 将src_title字段表头补全
    @api.multi
    def head_create(self):
        cpo_bom = self._context.get('active_id')  # 增加的
        self.update({'cpo_bom': cpo_bom})  # 增加的
        cpo_bom_file = self.cpo_bom.search([('id', '=', cpo_bom)])
        if cpo_bom_file:
            bom_list = []
            bom_ref = [{'src_title': x.src_title, 'cpo_title': x.cpo_title} for x in cpo_bom_file.bom_fields_line]
            bom_file = cpo_bom_file.bom_file
            if not bom_file:
                bom_file = self.env['ir.attachment'].search([('res_model', '=', 'cpo_offer_bom.bom'),
                                                             ('res_id', '=', cpo_bom)]).datas
            workbook = xlrd.open_workbook(file_contents=base64.decodestring(bom_file))
            head_count_repetition = int(self.cpo_title.search_count([('basedata_id', '=', self.id)]))
            if len(workbook._sheet_list) >= 1:
                workbook_content = workbook.sheet_by_index(0)
                ce_rows = []
                for x_row in range(0, workbook_content.nrows):
                    i_row = []
                    for y_col in range(workbook_content.ncols):
                        i_row.append(workbook_content.cell(x_row, y_col).value)
                    ce_rows.append(i_row)
                rows = recheck_bom_file_content(ce_rows)
                for x_str in rows[0]:
                    check_filter = filter(lambda x: x.get('src_title') == x_str, bom_ref)
                    if check_filter:
                        bom_list.append((0, 0, check_filter[0]))
                    else:
                        bom_list.append((0, 0, {'src_title': x_str}))
                return {'cpo_title': bom_list}
        return {}


class rfq_inherit_sale_order_bom(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        if vals.get('state') == 'wait_confirm':
            if self.order_line.bom_rootfile:
                self.order_line.bom_rootfile.write({'partner_id': self.partner_id.id, 'cpo_colour': 'ok', 'cpo_table_bom': True})
        return super(rfq_inherit_sale_order_bom, self).write(vals)


class BomSituation(models.Model):
    _name = 'bom.situation'
    _description = 'Dashboard'

    name = fields.Char('Name', translate=True, size=64)
    state = fields.Selection([('no', 'NO'), ('check', 'check'), ('complete', 'complete')], string='Bom Type')
    color = fields.Integer('Color')
    button_name = fields.Char('Name', compute='_compute_button_name')

    def _compute_button_name(self):
        data = self.env['cpo_offer_bom.bom']
        for x_id in self:
            if x_id.state == 'no':
                list_ids = data.search([('cpo_check_bom', '=', 'no_check')]).ids
                x_id.button_name = _('No need to check') + ' - ' + str(len(list_ids))
            elif x_id.state == 'check':
                list_ids = data.search(['|', ('cpo_check_bom', '=', 'ok_check'), ('state', '=', 'check')]).ids
                x_id.button_name = _('Waiting for inspection') + ' - ' + str(len(list_ids))
            elif x_id.state == 'complete':
                list_ids = data.search([('cpo_check_bom', '=', 'checked')]).ids
                x_id.button_name = _('Complete inspection') + ' - ' + str(len(list_ids))

    def action_button_name(self):
        action = None
        if self.state == 'no':
            action = self.env.ref('rfq_inherit_bom.offer_bom_no_check_action_window').read()[0]
        elif self.state == 'check':
            action = self.env.ref('rfq_inherit_bom.offer_bom_check_action_window').read()[0]
        elif self.state == 'complete':
            action = self.env.ref('rfq_inherit_bom.offer_bom_checked_action_window').read()[0]
        return action

