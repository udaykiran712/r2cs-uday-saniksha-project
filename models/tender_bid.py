from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class TenderBid(models.Model):
    _name = 'tender.bid'
    _description = 'Tender Bid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tender_no'

    tender_no = fields.Char(string='Tender Number', required=True)
    tender_ref = fields.Many2one('crm.lead', string='CRM Lead', required=True)
    project_type = fields.Selection([('civil', 'Civil'), ('pfb', 'Pre-Fab'), ('industrial', 'Industrial')],
                                    string='Project Type', required=True)
    currency_id = fields.Many2one('res.currency', related='tender_ref.currency_id', store=True, readonly=True)
    emd_amount = fields.Monetary(string='EMD Amount', currency_field='currency_id')
    bg_amount = fields.Monetary(string='Bank Guarantee Amount', currency_field='currency_id')
    submission_date = fields.Date(string='Submission Date', required=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('in_process', 'In Process'), ('submitted', 'Submitted'), ('won', 'Won'),
         ('lost', 'Lost')], string='Status', default='draft')
    estimated_value = fields.Monetary(string="Estimated Value", currency_field='currency_id')
    probability = fields.Integer(string='Probability %', default=0)
    close_reason = fields.Selection([
        ('price', 'Price'),
        ('scope', 'Out of Scope'),
        ('competitor', 'Competitor'),
        ('other', 'Other'),
    ], string='Close Reason')
    close_reason_note = fields.Text(string='Close Reason Note')
    stage_id = fields.Many2one('tender.stage', string='Stage', group_expand='_read_group_stage_ids')

    def _read_group_stage_ids(self, stages, order):
        return self.env['tender.stage'].search([], order=order)

    @api.model
    def create(self, vals):
        # On create, link tender_no to crm.lead name as reference
        # Additional constraints can be added here
        return super().create(vals)

    def action_mark_won(self):
        for record in self:
            if record.status == 'won':
                raise UserError("Tender is already marked as won.")
            record.status = 'won'

    def action_mark_lost(self):
        for record in self:
            if record.status == 'lost':
                raise UserError("Tender is already marked as lost.")
            if not record.close_reason:
                raise UserError("Please fill the 'Close Reason' before marking as lost.")
            record.status = 'lost'

    @api.model
    def cron_assign_upload_bg_activity(self):
        today = fields.Date.context_today(self)
        target_date = fields.Date.to_string(fields.Date.from_string(today) + timedelta(days=3))
        active_stage_ids = self.env['crm.stage'].search([('fold', '=', False)]).ids
        tenders = self.search([
            ('submission_date', '=', target_date),
            ('tender_ref.stage_id', 'in', active_stage_ids)
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        for tender in tenders:
            responsible_user = tender.tender_ref.user_id or self.env.user
            self.env['mail.activity'].create({
                'res_id': tender.id,
                'res_model_id': self.env['ir.model']._get(self._name).id,
                'activity_type_id': activity_type.id,
                'summary': 'Upload Bank Guarantee',
                'user_id': responsible_user.id,
                'date_deadline': tender.submission_date,
            })
