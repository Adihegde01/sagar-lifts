"""Purchase Invoice — Supplier Bills & Contractor Labour Bills.

One doctype, two purposes: a routine payable to a material Supplier, or a
labour payable to an installation Contractor. Bill Type is what tells
ERPNext — and the person raising it — which rules apply; everything else
here only appears/applies for a Contractor bill.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

IS_CONTRACTOR_BILL = 'eval:doc.bill_type=="Contractor"'

CUSTOM_FIELDS = {
	"Purchase Invoice": [
		{
			"fieldname": "bill_type",
			"label": "Bill Type",
			"fieldtype": "Select",
			"options": "Contractor\nSupplier",
			"reqd": 1,
			"description": "The person raising the bill picks one — everything else follows from this",
			"insert_after": "supplier_name",
		},
		# --- Sagar Lifts Billing tab --------------------------------------------
		# Bill Type stays on Details (it drives everything); the rest lives here,
		# between the native Details and Payments tabs.
		{
			"fieldname": "sl_billing_tab",
			"label": "Sagar Lifts Billing",
			"fieldtype": "Tab Break",
			"insert_after": "supplied_items",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"depends_on": IS_CONTRACTOR_BILL,
			"mandatory_depends_on": IS_CONTRACTOR_BILL,
			"in_standard_filter": 1,
			"description": "The deployment this labour bill is for — blank and irrelevant for a Supplier bill",
			"insert_after": "sl_billing_tab",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "job_number",
		},
		# --- Bill Verification (Contractor bills only) -----------------------
		{
			"fieldname": "sl_bill_verification_section",
			"label": "Bill Verification",
			"fieldtype": "Section Break",
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "job_name",
		},
		{
			"fieldname": "bill_submitted_by_contractor",
			"label": "Bill Submitted By Contractor",
			"fieldtype": "Date",
			"description": "Date the contractor submitted the bill",
			"insert_after": "sl_bill_verification_section",
		},
		{
			"fieldname": "bill_received_by",
			"label": "Bill Received By",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "bill_submitted_by_contractor",
		},
		{
			"fieldname": "bill_received_date",
			"label": "Bill Received Date",
			"fieldtype": "Date",
			"insert_after": "bill_received_by",
		},
		{
			"fieldname": "sl_bill_verification_col",
			"fieldtype": "Column Break",
			"insert_after": "bill_received_date",
		},
		{
			"fieldname": "bill_amount_as_per_contractor",
			"label": "Bill Amount as per Contractor (₹)",
			"fieldtype": "Currency",
			"insert_after": "sl_bill_verification_col",
		},
		{
			"fieldname": "bill_amount_agreed",
			"label": "Bill Amount Agreed (₹)",
			"fieldtype": "Currency",
			"insert_after": "bill_amount_as_per_contractor",
		},
		{
			"fieldname": "difference_amount",
			"label": "Difference Amount (₹)",
			"fieldtype": "Currency",
			"read_only": 1,
			"description": "Contractor's amount − Agreed amount, calculated on save",
			"insert_after": "bill_amount_agreed",
		},
		{
			"fieldname": "difference_reason",
			"label": "Difference Reason",
			"fieldtype": "Small Text",
			"insert_after": "difference_amount",
		},
		# --- Manufacturing Approval (Contractor bills only) ------------------
		{
			"fieldname": "sl_mfg_approval_section",
			"label": "Manufacturing Approval",
			"fieldtype": "Section Break",
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "difference_reason",
		},
		{
			"fieldname": "sent_to_manufacturing",
			"label": "Sent to Manufacturing for Approval",
			"fieldtype": "Check",
			"insert_after": "sl_mfg_approval_section",
		},
		{
			"fieldname": "sent_to_manufacturing_date",
			"label": "Sent to Manufacturing Date",
			"fieldtype": "Date",
			"read_only": 1,
			"description": "Auto-fills when sent",
			"insert_after": "sent_to_manufacturing",
		},
		{
			"fieldname": "approved_by_manufacturing",
			"label": "Approved by Manufacturing",
			"fieldtype": "Check",
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Manufacturing manager ticks this to approve",
			"insert_after": "sent_to_manufacturing_date",
		},
		{
			"fieldname": "manufacturing_approval_by",
			"label": "Manufacturing Approval By",
			"fieldtype": "Link",
			"options": "User",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Auto-fills on approval",
			"insert_after": "approved_by_manufacturing",
		},
		{
			"fieldname": "manufacturing_approval_date",
			"label": "Manufacturing Approval Date",
			"fieldtype": "Date",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Auto-fills on approval",
			"insert_after": "manufacturing_approval_by",
		},
		{
			"fieldname": "sl_mfg_approval_col",
			"fieldtype": "Column Break",
			"insert_after": "manufacturing_approval_date",
		},
		{
			"fieldname": "manufacturing_remarks",
			"label": "Manufacturing Remarks",
			"fieldtype": "Small Text",
			"insert_after": "sl_mfg_approval_col",
		},
		{
			"fieldname": "manufacturing_rejected",
			"label": "Manufacturing Rejected",
			"fieldtype": "Check",
			"insert_after": "manufacturing_remarks",
		},
		{
			"fieldname": "manufacturing_rejection_reason",
			"label": "Manufacturing Rejection Reason",
			"fieldtype": "Small Text",
			"depends_on": "manufacturing_rejected",
			"mandatory_depends_on": "manufacturing_rejected",
			"insert_after": "manufacturing_rejected",
		},
		# --- Labour Bill Tracking (Contractor bills only) --------------------
		# Percentages are of the Linked Sales Order's Contract Value (its Grand
		# Total); the cumulative figure counts every submitted contractor bill
		# on that order plus this one.
		{
			"fieldname": "sl_labour_bill_section",
			"label": "Labour Bill Tracking",
			"fieldtype": "Section Break",
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "manufacturing_rejection_reason",
		},
		{
			"fieldname": "labour_bill_percent",
			"label": "Labour Bill % of Contract Value",
			"fieldtype": "Float",
			"read_only": 1,
			"insert_after": "sl_labour_bill_section",
		},
		{
			"fieldname": "cumulative_labour_bills_percent",
			"label": "Cumulative Labour Bills %",
			"fieldtype": "Float",
			"read_only": 1,
			"insert_after": "labour_bill_percent",
		},
		{
			"fieldname": "labour_bill_within_limit",
			"label": "Labour Bill Within Limit",
			"fieldtype": "Check",
			"read_only": 1,
			"description": "Cumulative must stay at or under 100%",
			"insert_after": "cumulative_labour_bills_percent",
		},
		{
			"fieldname": "sl_labour_bill_col",
			"fieldtype": "Column Break",
			"insert_after": "labour_bill_within_limit",
		},
		{
			"fieldname": "over_limit_approval_by",
			"label": "Over Limit Approval By",
			"fieldtype": "Link",
			"options": "User",
			"depends_on": 'eval:doc.bill_type=="Contractor" && !doc.labour_bill_within_limit',
			"mandatory_depends_on": 'eval:doc.bill_type=="Contractor" && !doc.labour_bill_within_limit',
			"insert_after": "sl_labour_bill_col",
		},
		{
			"fieldname": "over_limit_approval_reason",
			"label": "Over Limit Approval Reason",
			"fieldtype": "Small Text",
			"depends_on": 'eval:doc.bill_type=="Contractor" && !doc.labour_bill_within_limit',
			"mandatory_depends_on": 'eval:doc.bill_type=="Contractor" && !doc.labour_bill_within_limit',
			"insert_after": "over_limit_approval_by",
		},
		# --- Payment Details (all bills) ---------------------------------------
		{
			"fieldname": "sl_payment_details_section",
			"label": "Payment Details",
			"fieldtype": "Section Break",
			"insert_after": "over_limit_approval_reason",
		},
		{
			"fieldname": "sl_payment_mode",
			"label": "Payment Mode",
			"fieldtype": "Select",
			"options": "\nBank Transfer\nCheque\nCash\nUPI\nNEFT\nRTGS",
			"allow_on_submit": 1,
			"insert_after": "sl_payment_details_section",
		},
		{
			"fieldname": "payment_reference",
			"label": "Payment Reference",
			"fieldtype": "Data",
			"allow_on_submit": 1,
			"insert_after": "sl_payment_mode",
		},
		{
			"fieldname": "payment_date",
			"label": "Payment Date",
			"fieldtype": "Date",
			"allow_on_submit": 1,
			"insert_after": "payment_reference",
		},
		{
			"fieldname": "sl_payment_details_col",
			"fieldtype": "Column Break",
			"insert_after": "payment_date",
		},
		{
			"fieldname": "payment_done_by",
			"label": "Payment Done By",
			"fieldtype": "Link",
			"options": "User",
			"allow_on_submit": 1,
			"insert_after": "sl_payment_details_col",
		},
		{
			"fieldname": "payment_notes",
			"label": "Payment Notes",
			"fieldtype": "Small Text",
			"allow_on_submit": 1,
			"insert_after": "payment_done_by",
		},
	]
}


def setup_purchase_invoice_customization():
	# Drop the earlier is_contractor_bill checkbox — superseded by Bill Type.
	frappe.db.delete("Custom Field", {"dt": "Purchase Invoice", "fieldname": "is_contractor_bill"})
	# Superseded by the Sagar Lifts Billing tab, which the Payments tab closes.
	frappe.db.delete("Custom Field", {"dt": "Purchase Invoice", "fieldname": "sl_bill_verification_end_section"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Purchase Invoice")
