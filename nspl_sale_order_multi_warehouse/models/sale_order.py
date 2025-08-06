from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string="Warehouses",
        domain="[('company_id', '=', company_id)]",
        help="Select multiple warehouses for this order line."
    )

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_count = fields.Integer(
        string="Delivery Count",
        compute='_compute_delivery_count',
        store=False,
        help="Number of delivery orders associated with this sale order."
    )

    @api.depends('picking_ids')
    def _compute_delivery_count(self):
        for order in self:
            order.delivery_count = self.env['stock.picking'].search_count([('origin', '=', order.name)])

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        grouped_lines = {}
        for line in self.order_line.filtered(lambda l: l.product_id.type == 'product'):
            # If no warehouses selected on line, fallback to order's warehouse
            warehouse_ids = line.warehouse_ids or self.warehouse_id
            for warehouse in warehouse_ids:
                warehouse_id = warehouse.id
                if warehouse_id not in grouped_lines:
                    grouped_lines[warehouse_id] = self.env['sale.order.line']
                grouped_lines[warehouse_id] += line

        for warehouse_id, lines in grouped_lines.items():
            self._create_custom_picking(lines, warehouse_id)
        return res

    def _create_custom_picking(self, lines, warehouse_id):
        warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        picking_vals = {
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'move_ids': [],
            'sale_id': self.id,
        }
        for line in lines:
            move = {
                'name': line.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'location_id': warehouse.lot_stock_id.id,
                'location_dest_id': self.partner_id.property_stock_customer.id,
                'picking_type_id': warehouse.out_type_id.id,
            }
            picking_vals['move_ids'].append((0, 0, move))
        picking = self.env['stock.picking'].create(picking_vals)
        return picking