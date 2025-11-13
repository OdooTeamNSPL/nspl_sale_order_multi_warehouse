from odoo import fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        help='Warehouse where product taken from')

    def _action_launch_stock_rule(self, *, previous_product_uom_qty=False):
        if self.env.context.get("skip_procurement"):
            return True

        precision = self.env['decimal.precision'].precision_get('Product Unit')
        procurements = []

        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or line.order_id.locked or line.product_id.type != 'consu':
                continue

            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            # ✅ Auto-set product warehouse before procurement
            if not line.product_warehouse_id:
                # Prefer product route warehouse or fallback to order warehouse
                warehouse = line.order_id.warehouse_id
                if not warehouse and line.order_id.picking_ids:
                    warehouse = line.order_id.picking_ids[0].picking_type_id.warehouse_id
                line.product_warehouse_id = warehouse

            # Create reference if needed
            if not line.order_id.stock_reference_ids:
                self.env['stock.reference'].create(line._prepare_reference_vals())

            # Procurement values
            values = line._prepare_procurement_values()
            if line.product_warehouse_id:
                values['warehouse_id'] = line.product_warehouse_id

            product_qty = line.product_uom_qty - qty
            line_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements += line._create_procurements(product_qty, procurement_uom, values)

        if procurements:
            self.env['stock.rule'].run(procurements)

        # Confirm related pickings
        for order in self.mapped('order_id'):
            pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                pickings_to_confirm.action_confirm()
        return True
