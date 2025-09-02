from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    tender_bid_ids = fields.One2many('tender.bid', 'tender_ref', string='Tender Bids')
    tender_no = fields.Char(string='Tender Number')
    emd_amount = fields.Monetary(string='EMD Amount', currency_field='currency_id')
    bg_amount = fields.Monetary(string='Bank Guarantee Amount', currency_field='currency_id')
    submission_date = fields.Date(string='Tender Submission Date')
    boq_line_ids = fields.One2many('tender.boq.line', 'lead_id', string="BOQ Lines")

    tender_bid_count = fields.Integer(string='Tender Bids', compute='_compute_tender_bid_count')
    boq_line_count = fields.Integer(string='BOQ Lines', compute='_compute_boq_line_count')

    @api.depends('tender_bid_ids')
    def _compute_tender_bid_count(self):
        for rec in self:
            rec.tender_bid_count = self.env['tender.bid'].search_count([('tender_ref', '=', rec.id)])

    @api.depends('boq_line_ids')
    def _compute_boq_line_count(self):
        for rec in self:
            rec.boq_line_count = self.env['tender.boq.line'].search_count([('lead_id', '=', rec.id)])

    def open_tender_bids(self):
        self.ensure_one()
        return {
            'name': 'Tender Bids',
            'type': 'ir.actions.act_window',
            'res_model': 'tender.bid',
            'view_mode': 'kanban,list,form',
            'target': 'current',
            'domain': [('tender_ref', '=', self.id)],
            'context': {'default_tender_ref': self.id},
        }

    def open_boq_lines(self):
        self.ensure_one()
        return {
            'name': 'BOQ Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'tender.boq.line',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }


class TenderBoqLine(models.Model):
    _name = 'tender.boq.line'
    _description = 'Tender BOQ Line'

    name = fields.Char(string='BOQ Number', required=True, copy=False, readonly=True, default='New')
    lead_id = fields.Many2one('crm.lead', string="Lead", ondelete='cascade', required=True)
    item_code = fields.Char(string="Item Code", required=True)
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", required=True)
    unit = fields.Char(string="Unit of Measure", required=True)
    rate = fields.Float(string="Rate", required=True)
    amount = fields.Float(string="Amount", required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tender.boq.line') or 'New'
        return super(TenderBoqLine, self).create(vals)
