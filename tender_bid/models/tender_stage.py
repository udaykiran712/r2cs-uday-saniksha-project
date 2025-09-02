from odoo import models, fields, api

class TenderStage(models.Model):
    _name = 'tender.stage'
    _description = 'Tender Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, help='Name of the tender stage')
    sequence = fields.Integer(string='Sequence', default=1, help='Used to order the stages')
    fold = fields.Boolean(string='Folded by Default', default=False, help='Whether the stage is folded in kanban view')

    # Optional: Add color field for visual distinction if needed
    color = fields.Integer(string='Color Index')
