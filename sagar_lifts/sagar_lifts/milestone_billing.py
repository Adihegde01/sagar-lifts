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
	for item in inv.items:
		rate = flt(item.rate * pct / 100, item.precision("rate"))
		item.rate = item.price_list_rate = rate
		item.discount_percentage = item.discount_amount = 0
	inv.run_method("calculate_taxes_and_totals")
	return inv
