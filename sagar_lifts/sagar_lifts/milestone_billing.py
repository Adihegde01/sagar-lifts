import frappe
from frappe import _
from frappe.utils import flt

from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

from sagar_lifts.sagar_lifts.setup.sales_order import MILESTONE_COUNT

MILESTONES = range(1, MILESTONE_COUNT + 1)


@frappe.whitelist()
def make_milestone_invoice(sales_order: str, milestone: int):
	"""Proforma Invoice for one payment milestone of a submitted Sales Order.

	ERPNext's own Sales Order -> Sales Invoice mapping bills the whole order;
	this scales every line to the milestone's share (Advance 20%, On Delivery
	30%, ...) and returns it unsaved for Billing to review.
	"""
	milestone = int(milestone)
	if milestone not in MILESTONES:
		frappe.throw(_("Unknown milestone {0}").format(milestone))

	so = frappe.get_doc("Sales Order", sales_order)
	so.check_permission("read")
	if so.docstatus != 1:
		frappe.throw(_("Submit the Sales Order before raising its invoices."))

	name = so.get(f"milestone_{milestone}_name")
	pct = flt(so.get(f"milestone_{milestone}_percent"))
	if not pct:
		frappe.throw(_("Milestone {0} has no percentage on this order.").format(milestone))

	existing = frappe.db.get_value(
		"Sales Invoice",
		{"job_id": so.name, "docstatus": ["<", 2], "pi_type": "Proforma Invoice", "milestone_number": str(milestone)},
		"name",
	)
	if existing:
		frappe.throw(
			_("Milestone {0} ({1}) is already invoiced on {2}.").format(milestone, name, existing)
		)

	inv = make_sales_invoice(so.name)
	inv.pi_type = "Proforma Invoice"
	inv.billing_trigger_type = "Milestone"
	inv.job_id = so.name
	# milestone_number/percent drive the invoice print's milestone table (invoice_print.py)
	inv.milestone_number = str(milestone)
	inv.milestone_name = name
	inv.milestone_percent = pct
	inv.remarks = f"Milestone {milestone} — {name} ({pct:g}%) of {so.name}"
	# ERPNext maps "qty still to bill" = ordered qty minus qty already billed.
	# We bill by scaling the rate and keep the full qty, so once the first
	# milestone is submitted that works out to 0 and the next milestone opened
	# with no usable rows. Rebuild qty and rate from the order line itself.
	order_rows = {row.name: row for row in so.items}
	for item in inv.items:
		row = order_rows.get(item.so_detail)
		if not row:
			continue
		item.qty = row.qty
		item.rate = item.price_list_rate = flt(row.rate * pct / 100, item.precision("rate"))
		item.discount_percentage = item.discount_amount = 0
	inv.run_method("calculate_taxes_and_totals")
	return inv


CONFIRM_ORDER_ROLES = ("SL Sales Admin", "SL Billing", "SL Manufacturing", "SL Admin", "System Manager")


@frappe.whitelist()
def confirm_order(sales_order: str):
	"""Submit a draft Sales Order straight into Active.

	The order workflow has no screen action for submitting a draft (see the
	Draft state in setup/deployment_workflow.py); this is the same step as a
	plain Submit, limited to the teams that confirm orders.
	"""
	frappe.only_for(CONFIRM_ORDER_ROLES)
	so = frappe.get_doc("Sales Order", sales_order)
	so.check_permission("submit")
	if so.docstatus != 0:
		frappe.throw(_("{0} is already submitted.").format(so.name))
	so.deployment_status = "Active"
	so.submit()
	return so.name
