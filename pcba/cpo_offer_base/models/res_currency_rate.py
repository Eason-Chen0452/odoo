from odoo import api, fields, models, tools, _
import time

class CurrencyRate(models.Model):
    _inherit = ['res.currency.rate', 'mail.thread', 'mail.activity.mixin']
    _name="res.currency.rate"

    @api.model
    def default_get(self, fields_list):
        res = super(CurrencyRate, self).default_get(fields_list)
        if self.env.context.get('cpo_only_usd_currency'):
            res.update({
                'currency_id': self.env.ref("base.USD").id
            })
        return res

    @api.multi
    def write(self, vals):
        for row in self:
            msg = _("Currency Rate From {src} change to {des},time:{time}").format(src=row.rate,des=vals.get('rate'),time=time.strftime("%Y-%m-%d %H:%M:%S"))
            row.message_post(body=msg)
        return super(CurrencyRate, self).write(vals)
