"""Sales Invoice — Proforma & Tax Invoice.

PI Type and the Sales Order link aren't in the guide's Section 5 table but
Steps 28-29 depend on them (Section 5, Open Items) — every PI/TI must link
back to a Sales Order.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Sales Invoice": [
		# --- Invoice Classification -------------------------------------------
		{
			"fieldname": "sl_invoice_classification_section",
			"label": "Invoice Classification",
			"fieldtype": "Section Break",
			"insert_after": "customer_name",
		},
		{
			# Fieldname stays pi_type — naming series and tasks.py key off it.
			"fieldname": "pi_type",
			"label": "Invoice Type",
			"fieldtype": "Select",
			"options": "Proforma Invoice\nTax Invoice",
			"reqd": 1,
			"description": "Decides which Naming Series applies",
			"insert_after": "sl_invoice_classification_section",
		},
		{
			"fieldname": "billing_trigger_type",
			"label": "Billing Trigger Type",
			"fieldtype": "Select",
			"options": "\nMilestone\nAMC Quarterly\nJumping\nSpare Parts\nDismantling\nVariation\nRepair",
			"reqd": 0,
			# Required on drafts only, so records submitted before this field
			# existed can still be updated (workflow moves, after-submit edits).
			"mandatory_depends_on": "eval:doc.docstatus==0",
			"insert_after": "pi_type",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"in_standard_filter": 1,
			"description": "Every PI/TI must be linked to a Sales Order",
			"insert_after": "billing_trigger_type",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"insert_after": "job_number",
		},
		{
			"fieldname": "sl_invoice_classification_col",
			"fieldtype": "Column Break",
			"insert_after": "job_name",
		},
		{
			"fieldname": "developer_name",
			"label": "Developer Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.developer_name",
			"fetch_if_empty": 1,
			"insert_after": "sl_invoice_classification_col",
		},
		{
			"fieldname": "site_name",
			"label": "Site Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.site_name",
			"fetch_if_empty": 1,
			"insert_after": "developer_name",
		},
		# --- Milestone Billing (Billing Trigger Type = Milestone) -------------
		{
			"fieldname": "sl_milestone_billing_section",
			"label": "Milestone Billing",
			"fieldtype": "Section Break",
			"depends_on": 'eval:doc.billing_trigger_type=="Milestone"',
			"insert_after": "site_name",
		},
		{
			"fieldname": "milestone_number",
			"label": "Milestone Number",
			"fieldtype": "Select",
			"options": "\n1\n2\n3\n4\n5",
			"insert_after": "sl_milestone_billing_section",
		},
		{
			"fieldname": "milestone_name",
			"label": "Milestone Name",
			"fieldtype": "Data",
			"description": "Filled from the Sales Order's Payment Milestones on save",
			"insert_after": "milestone_number",
		},
		{
			"fieldname": "milestone_percent",
			"label": "Milestone %",
			"fieldtype": "Percent",
			"description": "Filled from the Sales Order's Payment Milestones on save",
			"insert_after": "milestone_name",
		},
		{
			"fieldname": "sl_milestone_billing_col",
			"fieldtype": "Column Break",
			"insert_after": "milestone_percent",
		},
		{
			"fieldname": "milestone_requested_by",
			"label": "Milestone Requested By",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "sl_milestone_billing_col",
		},
		{
			"fieldname": "milestone_request_date",
			"label": "Milestone Request Date",
			"fieldtype": "Date",
			"insert_after": "milestone_requested_by",
		},
		{
			"fieldname": "milestone_request_department",
			"label": "Milestone Request Department",
			"fieldtype": "Select",
			"options": "\nManufacturing\nDispatch\nService\nAdmin",
			"insert_after": "milestone_request_date",
		},
		# --- AMC Billing (Billing Trigger Type = AMC Quarterly) ---------------
		{
			"fieldname": "sl_amc_billing_section",
			"label": "AMC Billing",
			"fieldtype": "Section Break",
			"depends_on": 'eval:doc.billing_trigger_type=="AMC Quarterly"',
			"insert_after": "milestone_request_department",
		},
		{
			"fieldname": "amc_quarter",
			"label": "AMC Quarter",
			"fieldtype": "Select",
			"options": "\nQ1\nQ2\nQ3\nQ4",
			"description": "Auto-fills from AMC Period From (Indian FY quarters)",
			"insert_after": "sl_amc_billing_section",
		},
		{
			"fieldname": "amc_period_from",
			"label": "AMC Period From",
			"fieldtype": "Date",
			"insert_after": "amc_quarter",
		},
		{
			"fieldname": "amc_period_to",
			"label": "AMC Period To",
			"fieldtype": "Date",
			"description": "Defaults to the end of that quarter",
			"insert_after": "amc_period_from",
		},
		{
			"fieldname": "sl_amc_billing_col",
			"fieldtype": "Column Break",
			"insert_after": "amc_period_to",
		},
		{
			"fieldname": "amc_monthly_rate",
			"label": "AMC Monthly Rate (₹)",
			"fieldtype": "Currency",
			"fetch_from": "job_id.monthly_amc_rate",
			"fetch_if_empty": 1,
			"insert_after": "sl_amc_billing_col",
		},
		{
			"fieldname": "amc_months_billed",
			"label": "AMC Months Billed",
			"fieldtype": "Int",
			"read_only": 1,
			"description": "Calendar months covered by the period, calculated on save",
			"insert_after": "amc_monthly_rate",
		},
		# --- Jumping Billing (Billing Trigger Type = Jumping) ------------------
		{
			"fieldname": "sl_jumping_billing_section",
			"label": "Jumping Billing",
			"fieldtype": "Section Break",
			"depends_on": 'eval:doc.billing_trigger_type=="Jumping"',
			"insert_after": "amc_months_billed",
		},
		{
			"fieldname": "jumping_reference",
			"label": "Jumping Reference",
			"fieldtype": "Data",
			"insert_after": "sl_jumping_billing_section",
		},
		{
			"fieldname": "jumping_date",
			"label": "Jumping Date",
			"fieldtype": "Date",
			"insert_after": "jumping_reference",
		},
		{
			"fieldname": "sl_jumping_billing_col",
			"fieldtype": "Column Break",
			"insert_after": "jumping_date",
		},
		{
			"fieldname": "jumping_from_floor",
			"label": "Jumping From Floor",
			"fieldtype": "Int",
			"insert_after": "sl_jumping_billing_col",
		},
		{
			"fieldname": "jumping_to_floor",
			"label": "Jumping To Floor",
			"fieldtype": "Int",
			"insert_after": "jumping_from_floor",
		},
		# --- PI to TI Conversion (Tax Invoices only) ---------------------------
		{
			"fieldname": "sl_pi_to_ti_section",
			"label": "PI to TI Conversion",
			"fieldtype": "Section Break",
			"depends_on": 'eval:doc.pi_type=="Tax Invoice"',
			"insert_after": "jumping_to_floor",
		},
		{
			"fieldname": "original_pi_number",
			"label": "Original PI Number",
			"fieldtype": "Data",
			"description": "Free text so paper-era PIs can be entered too",
			"insert_after": "sl_pi_to_ti_section",
		},
		{
			"fieldname": "pi_date",
			"label": "PI Date",
			"fieldtype": "Date",
			"description": "Auto-fills when the PI Number matches a Proforma Invoice in the system",
			"insert_after": "original_pi_number",
		},
		{
			"fieldname": "sl_pi_to_ti_col",
			"fieldtype": "Column Break",
			"insert_after": "pi_date",
		},
		{
			"fieldname": "ti_raised_against_full_pi",
			"label": "TI Raised Against Full PI",
			"fieldtype": "Check",
			"insert_after": "sl_pi_to_ti_col",
		},
		{
			"fieldname": "part_payment_ti",
			"label": "Part Payment TI",
			"fieldtype": "Check",
			"insert_after": "ti_raised_against_full_pi",
		},
		{
			"fieldname": "part_payment_amount",
			"label": "Part Payment Amount (₹)",
			"fieldtype": "Currency",
			"depends_on": "part_payment_ti",
			"mandatory_depends_on": "part_payment_ti",
			"insert_after": "part_payment_ti",
		},
		# --- Outstanding Tracking ---------------------------------------------
		{
			"fieldname": "sl_outstanding_tracking_section",
			"label": "Outstanding Tracking",
			"fieldtype": "Section Break",
			"insert_after": "part_payment_amount",
		},
		{
			"fieldname": "previous_pi_outstanding",
			"label": "Previous PI Outstanding",
			"fieldtype": "Check",
			"read_only": 1,
			"description": "Auto: this developer has other unpaid submitted invoices",
			"insert_after": "sl_outstanding_tracking_section",
		},
		{
			"fieldname": "previous_outstanding_amount",
			"label": "Previous Outstanding Amount (₹)",
			"fieldtype": "Currency",
			"read_only": 1,
			"insert_after": "previous_pi_outstanding",
		},
		{
			"fieldname": "outstanding_warning_acknowledged",
			"label": "Outstanding Warning Acknowledged",
			"fieldtype": "Check",
			"depends_on": "previous_pi_outstanding",
			"description": "Must be ticked before submitting while the developer has unpaid invoices",
			"insert_after": "previous_outstanding_amount",
		},
		{
			"fieldname": "outstanding_warning_acknowledged_by",
			"label": "Outstanding Warning Acknowledged By",
			"fieldtype": "Link",
			"options": "User",
			"read_only": 1,
			"depends_on": "outstanding_warning_acknowledged",
			"insert_after": "outstanding_warning_acknowledged",
		},
		{
			"fieldname": "sl_outstanding_tracking_col",
			"fieldtype": "Column Break",
			"insert_after": "outstanding_warning_acknowledged_by",
		},
		{
			"fieldname": "days_outstanding",
			"label": "Days Outstanding",
			"fieldtype": "Int",
			"read_only": 1,
			"allow_on_submit": 1,
			"description": "Days past the due date while unpaid — refreshed daily",
			"insert_after": "sl_outstanding_tracking_col",
		},
		{
			"fieldname": "escalation_level",
			"label": "Escalation Level",
			"fieldtype": "Select",
			"options": "None\nLevel 1 — CL\nLevel 2 — Billing\nLevel 3 — Management\nLevel 4 — Bad Debt",
			"default": "None",
			"read_only": 1,
			"allow_on_submit": 1,
			"description": "1–6 days overdue: L1 · 7–14: L2 · 15–89: L3 · 90+: L4 — refreshed daily",
			"insert_after": "days_outstanding",
		},
		# --- Billing Notes ------------------------------------------------------
		{
			"fieldname": "sl_billing_notes_section",
			"label": "Billing Notes",
			"fieldtype": "Section Break",
			"insert_after": "escalation_level",
		},
		{
			"fieldname": "billing_notes",
			"label": "Billing Notes",
			"fieldtype": "Small Text",
			"allow_on_submit": 1,
			"insert_after": "sl_billing_notes_section",
		},
		{
			"fieldname": "special_payment_instructions",
			"label": "Special Payment Instructions",
			"fieldtype": "Small Text",
			"allow_on_submit": 1,
			"insert_after": "billing_notes",
		},
		{
			"fieldname": "sl_billing_notes_col",
			"fieldtype": "Column Break",
			"insert_after": "special_payment_instructions",
		},
		{
			"fieldname": "dispute_raised",
			"label": "Dispute Raised",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"insert_after": "sl_billing_notes_col",
		},
		{
			"fieldname": "dispute_notes",
			"label": "Dispute Notes",
			"fieldtype": "Small Text",
			"allow_on_submit": 1,
			"depends_on": "dispute_raised",
			"insert_after": "dispute_raised",
		},
		{
			"fieldname": "dispute_resolved",
			"label": "Dispute Resolved",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"depends_on": "dispute_raised",
			"insert_after": "dispute_notes",
		},
	]
}

# --- Collection tab (between Details and Payments) ------------------------------
# Structured follow-up data; the narrative of each call/visit goes in the
# document's own Comment timeline. All editable after submit — collection
# work happens on submitted invoices.
CL_CONTACT_TYPES = "\nVisit\nPhone Call\nWhatsApp\nEmail\nMeeting"
ACCOUNTS_CONTACT_TYPES = "\nPhone Call\nWhatsApp\nEmail\nSMS"
_COMMITTED = "payment_commitment_received"
_ESCALATED = "escalated_to_management"
_collection_fields = [
	{"fieldname": "sl_collection_tab", "label": "Collection", "fieldtype": "Tab Break", "insert_after": "total_billing_amount"},
	# Moved here from Invoice Classification.
	{
		"fieldname": "collection_lead",
		"label": "Collection Lead",
		"fieldtype": "Link",
		"options": "User",
		"fetch_from": "job_id.collection_lead",
		"read_only": 1,
		"description": "Fetched from the Job — the escalation ladder routes reminders to this user",
	},
	{
		"fieldname": "accounts_caller",
		"label": "Accounts Caller",
		"fieldtype": "Link",
		"options": "User",
		"length": 100,
		"description": "Defaults to the user holding the SL Accounts Caller role",
	},
	{"fieldname": "last_cl_contact_date", "label": "Last CL Contact Date", "fieldtype": "Date"},
	{"fieldname": "last_cl_contact_type", "label": "Last CL Contact Type", "fieldtype": "Select", "options": CL_CONTACT_TYPES, "length": 20},
	{"fieldname": "last_accounts_call_date", "label": "Last Accounts Call Date", "fieldtype": "Date"},
	{
		"fieldname": "last_accounts_contact_type",
		"label": "Last Accounts Contact Type",
		"fieldtype": "Select",
		"options": ACCOUNTS_CONTACT_TYPES,
		"length": 20,
	},
	{
		"fieldname": "collection_status",
		"label": "Collection Status",
		"fieldtype": "Select",
		"options": "\nNot Started\nIn Follow Up\nCommitment Received\nPartially Paid\nPaid\nDisputed\nBad Debt Risk",
		"length": 30,
	},
	{"fieldname": "sl_collection_col_1", "fieldtype": "Column Break"},
	{"fieldname": _COMMITTED, "label": "Payment Commitment Received", "fieldtype": "Check"},
	{"fieldname": "payment_committed_amount", "label": "Payment Committed Amount (₹)", "fieldtype": "Currency", "depends_on": _COMMITTED},
	{"fieldname": "payment_committed_date", "label": "Payment Committed Date", "fieldtype": "Date", "depends_on": _COMMITTED},
	{"fieldname": "commitment_given_by", "label": "Commitment Given By", "fieldtype": "Data", "length": 100, "depends_on": _COMMITTED},
	{"fieldname": "commitment_fulfilled", "label": "Commitment Fulfilled", "fieldtype": "Check", "depends_on": _COMMITTED},
	{"fieldname": "sl_collection_col_2", "fieldtype": "Column Break"},
	{"fieldname": _ESCALATED, "label": "Escalated to Management", "fieldtype": "Check"},
	{
		"fieldname": "escalation_date",
		"label": "Escalation Date",
		"fieldtype": "Date",
		"read_only": 1,
		"depends_on": _ESCALATED,
		"description": "Auto-fills when escalated",
	},
	{"fieldname": "escalation_reason", "label": "Escalation Reason", "fieldtype": "Small Text", "depends_on": _ESCALATED, "mandatory_depends_on": _ESCALATED},
	{"fieldname": "next_follow_up_date", "label": "Next Follow Up Date", "fieldtype": "Date"},
	{
		"fieldname": "next_follow_up_by",
		"label": "Next Follow Up By",
		"fieldtype": "Select",
		"options": "\nCollection Lead\nAccounts Caller\nBoth\nManagement",
		"length": 20,
	},
	{"fieldname": "collection_notes", "label": "Collection Notes", "fieldtype": "Small Text"},
]
for _prev, _field in zip(_collection_fields, _collection_fields[1:]):
	_field["insert_after"] = _prev["fieldname"]
for _field in _collection_fields[1:]:
	# Read-only ones too: Escalation Date is stamped on already-submitted invoices.
	if _field["fieldtype"] != "Column Break":
		_field["allow_on_submit"] = 1
CUSTOM_FIELDS["Sales Invoice"] += _collection_fields


def setup_sales_invoice_customization():
	frappe.db.delete("Custom Field", {"dt": "Sales Invoice", "fieldname": "sl_invoice_classification_end_section"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
