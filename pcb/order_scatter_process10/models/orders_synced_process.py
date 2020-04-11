# -*- coding: utf-8 -*-

import logging, xmlrpclib
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SyncedSaleOrder(models.Model):
    _inherit = 'sale.order'

    synced_bool = fields.Boolean('Synced', default=False)
    synced_str = fields.Char('Synced', translate=True)

    def CheckSellerCode(self, seller_code):
        server = self.env['send.process.server'].search([])
        assert len(server) == 1, _('Multiple servers detected, system cannot identify which server to sync')
        value = server.SortOutValue()
        try:
            value = server.ConnErp(value)
            sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (value.get('host'), value.get('port')))
            sock = sock.execute(value.get('db'), value.get('uid'), value.get('pwd'), value.get('model'), 'SearchSellerCode', seller_code)
            if sock:
                return False, sock
            return _('No sales customer code in board factory is "%s"' % seller_code), sock
        except Exception as e:
            e = e.message if e.message else str(e)
            _logger.error(e)
            if value.get('conn') is False:
                return _('Test connection error, please determine whether the target host server is running normally; or the port number and target address are correct. The error is as follows: \n%s' % e), False
            elif value.get('install') is False:
                return _('The communication connection is successful, but the other party may not have the required module installed. The error is as follows: \n%s' % e), False
            else:
                return e, False

    @api.multi
    def SyncedOrder(self):
        seller_code = self.env['cpo_sale_allocations.allocations'].search([('name', '=', self._uid)]).seller_code
        message, value = self.CheckSellerCode(seller_code)
        if message and not value:
            raise ValidationError(message)
        self.env['orders.synced.process'].ApplyOrderSynced(order_id=self.id, seller_code=seller_code)
        self.SyncedInfo()

    def SyncedInfo(self, *args):
        value = {}
        if not self.synced_bool:
            value.update({'synced_bool': True})
        if args:
            pass
        self.write(value)

    # # 手动制造中 - 判断 是不是要PCB
    # @api.multi
    # def action_manufacturing(self):
    #     self.write({'state': 'manufacturing'})

    @api.multi
    def SyncProductStatus(self):
        # self
        pass


class MakeFlow(models.Model):
    _name = 'make.flow'
    _description = 'Production Process Information'

    name = fields.Char('Name', size=64)
    flow_time = fields.Datetime('Make Time')
    synced_id = fields.Many2one('orders.synced.process', 'Sale Order', index=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', related='synced_id.order_id')
    record = fields.Boolean('Recorded', default=False)


class OrdersSyncedProcess(models.Model):
    _name = 'orders.synced.process'
    _description = 'Orders Synced Process'
    _order = 'id desc'

    make_ids = fields.One2many('make.flow', 'synced_id', 'Production Process Information', auto_join=True)
    remark = fields.Text('Remark')
    product_state = fields.Char('Product State')
    name = fields.Char('Sync Number', index=True, readonly=True, size=64)
    seller_code = fields.Char('Board Factory Seller Code', index=True)
    state = fields.Selection([
        ('Just Create', 'Just Create'),
        ('Checked', 'Checked'),
        ('Production Status', 'Production Status'),
    ], string='Status', default='Just Create')
    order_id = fields.Many2one('sale.order', 'Sale Order', index=True, ondelete='cascade')
    order_state = fields.Selection(string='Order Status', related='order_id.state')
    file_id = fields.Many2many('ir.attachment', string='File', compute='_get_quote_file', store=True)
    quote_line_id = fields.Many2one('sale.quotation.line', string='PCB Quotation Line', compute='_get_quote_file', store=True)
    order_date = fields.Datetime('Confirmation Date', related='order_id.confirmation_date')
    order_create_time = fields.Datetime('Create Time', related='order_id.create_date')
    thick = fields.Float(string='PCB Thickness', digits=(16, 2), related='quote_line_id.thickness')
    cpo_length = fields.Float(string='Width/mm', digits=(16, 2), related='quote_line_id.cpo_length')
    cpo_width = fields.Float(string='Length/mm', digits=(16, 2), related='quote_line_id.cpo_width')
    inner = fields.Float(string='Inner Copper', digits=(16, 2), related='quote_line_id.inner_copper')
    outer = fields.Float(string='Outer Copper', digits=(16, 2), related='quote_line_id.outer_copper')
    surface_id = fields.Many2one('cam.surface.process', string='Surface Process', related='quote_line_id.surface')
    layer_id = fields.Many2one('cam.layer.number', string='Layer Number', related='quote_line_id.layer_number')
    base_id = fields.Many2one('cam.base.type', string='Copper Base Type', related='quote_line_id.base_type')
    via_id = fields.Many2one('cam.via.process', string='Via', related='quote_line_id.via_process')
    process_ids = fields.Many2many('cam.special.process', string='Special Processes', related='quote_line_id.sprocess_ids')
    material_ids = fields.Many2many('cam.special.material', string='Special Material', related='quote_line_id.smaterial_ids')
    mask_id = fields.Many2one('cam.ink.color', string='Solder Mask Color', related='quote_line_id.silkscreen_color')
    text_id = fields.Many2one('cam.ink.color', string='Silkscreen Color', related='quote_line_id.text_color')
    # volume_type = fields.Selection(VOLUME_TYPE, string='Volume Type', related='quote_line_id.volume_type')
    volume_type = fields.Selection(string='Volume Type', related='quote_line_id.volume_type')
    uom_qty = fields.Float(string='Quantity', related='quote_line_id.product_uom_qty')
    pcs_number = fields.Float(string='PCS Number', related='quote_line_id.pcs_number')
    pcs_per_set = fields.Integer(string='PCS Number Per Set', related='quote_line_id.pcs_per_set')
    # manner_uos = fields.Selection(AVAILABLE_UOS, string="Delivery UOS", related='quote_line_id.pcb_delivery_uos')
    manner_uos = fields.Selection(string="Delivery UOS", related='quote_line_id.pcb_delivery_uos')
    spell = fields.Integer(string='Combine Number', related='quote_line_id.combine_number')
    core = fields.Integer(string='Core Number', related='quote_line_id.cpo_core_number')
    pp = fields.Integer(string='PP Number', related='quote_line_id.cpo_pp_number')
    ipc_id = fields.Many2one('cam.acceptance.criteria', string='Acceptance Criteria', related='quote_line_id.cpo_standard')
    core_thick = fields.Float(string='Core Thick', digits=(16, 2), related='quote_line_id.core_thick')
    rogers_number = fields.Integer(string='Rogers Number', digits=(16, 2), related='quote_line_id.rogers_number')
    cnc = fields.Boolean(string='CNC', related='quote_line_id.cnc')
    test_stand = fields.Boolean(string='Test Stand', related='quote_line_id.tooling')
    stand_source = fields.Selection(string='Test Stand Source', related='quote_line_id.tooling_source')
    # stand_source = fields.Selection(STAND_SOURCE, string='Test Stand Source', related='quote_line_id.tooling_source')
    fly_probe = fields.Boolean(string='Fly Probe', related='quote_line_id.fly_probe')
    sink_gold = fields.Float(string='Sink Gold Thick', digits=(16, 2), related='quote_line_id.gold_thickness')
    # nickel_thick = fields.Selection(NICKEL_THICK, string='Nickel Thick', related='quote_line_id.cpo_nickel_thickness')
    nickel_thick = fields.Selection(string='Nickel Thick', related='quote_line_id.cpo_nickel_thickness')
    gold_size = fields.Float(string='Gold Size', digits=(16, 2), related='quote_line_id.gold_size')
    min_width = fields.Float(string='Min Line Width', digits=(16, 2), related='quote_line_id.min_line_cpo_width')
    min_space = fields.Float(string='Min Line Space', digits=(16, 2), related='quote_line_id.min_line_distance')
    min_hole = fields.Float(string='Min Hole', digits=(16, 2), related='quote_line_id.min_hole')
    gold_height = fields.Float(string='Gold Height', digits=(16, 2), related='quote_line_id.cpo_gold_height')
    gold_width = fields.Float(string='Gold Width', digits=(16, 2), related='quote_line_id.cpo_gold_width')
    gold_thick = fields.Float(string='Gold Thick / μ"', digits=(16, 2), related='quote_line_id.cpo_gold_thick')
    gold_root = fields.Float(string='Gold Root', digits=(16, 2), related='quote_line_id.cpo_gold_root')
    hole_space = fields.Float(string='Line To Hole Distance', digits=(16, 2), related='quote_line_id.line_to_hole_distance')
    hole_copper = fields.Float(string='Hole Copper', digits=(16, 2), related='quote_line_id.cpo_hole_copper')
    test_point = fields.Integer(string='ETest Points', related='quote_line_id.test_points')
    total_hole = fields.Integer(string='Total Holes', related='quote_line_id.total_holes')

    @api.model
    def create(self, vals):
        vals.update({'name': self._get_key_value()})
        return super(OrdersSyncedProcess, self).create(vals)

    # YY MM DD XXX
    def _get_key_value(self):
        x_str = ''.join(str(fields.date.today()).split('-'))[2:]
        num = str(self.search_count([('name', 'like', x_str)]) + 1)
        if len(num) == 1:
            x_str += '00' + num
        elif len(num) == 2:
            x_str += '0' + num
        else:
            x_str += num
        return x_str

    # 在正确的流程上 此时的order 一定是有附件的
    @api.depends('order_id')
    def _get_quote_file(self):
        for x_id in self:
            if not x_id.order_id:
                continue
            self._cr.execute("SELECT ID FROM IR_ATTACHMENT WHERE RES_MODEL='sale.order' AND RES_ID=%s" % x_id.order_id.id)
            x_list = self._cr.dictfetchall()
            x_list = [x.get('id') for x in x_list]
            x_id.update({'quote_line_id': x_id.order_id.quotation_line.id, 'file_id': [(6, 0, x_list)]})
        return True

    # 自动处理同步数据
    def ApplyOrderSynced(self, order_id=False, seller_code=False):
        if not order_id:
            order = self.env['sale.order'].search([('state', '=', 'manufacturing')])
            order = order.filtered(lambda x: x.quotation_line and x.product_type not in ['Stencil', 'PCBA'])
            for x_id in order:
                self.create({'order_id': x_id.id, 'seller_code': 'cpo-sales001'})
            return True
        self.create({'order_id': order_id, 'seller_code': seller_code})
        return True

    # 搜索订单号, 返回的订单下产品状态的条数
    @api.model
    def SearchOrderID(self, code):
        synced = self.search([('name', '=', code)])
        if synced.state != 'Production Status':
            synced.write({'state': 'Production Status'})
        make_ids = synced.make_ids
        return len(make_ids), synced.id

    # 更新同步产品状态
    @api.multi
    def UpdateProductState(self, value):
        make = self.env['make.flow']
        synced_id = self.id
        for x in value:
            make.create({
                'flow_time': x.get('create_date'),
                'name': x.get('name'),
                'synced_id': synced_id
            })
        return True

    # 基材 搜索 SQL
    def base_type_sql(self, x_id):
        self._cr.execute("SELECT NAME FROM CAM_BASE_TYPE WHERE ID=%s" % x_id)
        return self._cr.dictfetchall()[0].get('name')

    # 过孔处理 搜索 SQL
    def via_process_sql(self, x_id):
        self._cr.execute("SELECT NAME FROM CAM_VIA_PROCESS WHERE ID=%s" % x_id)
        return self._cr.dictfetchall()[0].get('name')

    # 特殊工艺 搜索 SQL
    def special_process_sql(self, x_ids):
        x_str = "="
        if len(x_ids) > 1:
            x_str, x_ids = "IN", tuple(x_ids)
        else:
            x_ids = x_ids[0]
        self._cr.execute("SELECT NAME FROM CAM_SPECIAL_PROCESS WHERE ID %s %s" % (x_str, x_ids, ))
        return [x.get('name') for x in self._cr.dictfetchall()]

    # 特殊材料 搜索 SQL
    def special_material_sql(self, x_ids):
        x_str = "="
        if len(x_ids) > 1:
            x_str, x_ids = "IN", tuple(x_ids)
        else:
            x_ids = x_ids[0]
        self._cr.execute("SELECT NAME FROM CAM_SPECIAL_MATERIAL WHERE ID %s %s" % (x_str, x_ids, ))
        return [x.get('name') for x in self._cr.dictfetchall()]

    # 阻焊颜色 - id
    def mask_color_sql(self, x_id):
        self._cr.execute("SELECT NAME FROM CAM_INK_COLOR WHERE ID=%s" % x_id)
        return self._cr.dictfetchall()[0].get('name')

    # 文字颜色 - id
    def text_color_sql(self, x_id):
        self._cr.execute("SELECT NAME FROM CAM_INK_COLOR WHERE ID=%s" % x_id)
        return self._cr.dictfetchall()[0].get('name')

    # 验收标准 - id
    def acceptance_criteria_sql(self, x_id):
        self._cr.execute("SELECT NAME FROM CAM_ACCEPTANCE_CRITERIA WHERE ID=%s" % x_id)
        return self._cr.dictfetchall()[0].get('name')



