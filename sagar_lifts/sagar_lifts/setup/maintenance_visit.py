"""Maintenance Visit — PM Visit.

Covers PM, Breakdown and Inspection visits with the same mandatory fields.
This is the one doctype SL Technician touches, logged from the mobile app on
their own assigned visits only. Visit Photos/Documents use the standard
Attachments panel — no custom field needed for that.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Maintenance Visit": [
		{
			"fieldname": "sl_pm_visit_section",
			"label": "PM Visit",
			"fieldtype": "Section Break",
			"insert_after": "purposes",
		},
		{
			"fieldname": "visit_type",
			"label": "Visit Type",
			"fieldtype": "Select",
			"options": "Preventive Maintenance\nBreakdown\nInspection",
			"reqd": 1,
			"description": "The Technician picks this when logging a PM visit or a breakdown call",
			"insert_after": "sl_pm_visit_section",
		},
		{
			"fieldname": "senior_technician",
			"label": "Senior Technician",
			"fieldtype": "Link",
			"options": "User",
			"reqd": 1,
			"description": "Must be selected from the registered technician list",
			"insert_after": "visit_type",
		},
		{
			"fieldname": "spares_used",
			"label": "Spares Used",
			"fieldtype": "Select",
			"options": "No Spares Used\nSpares Used",
			"reqd": 1,
			"insert_after": "senior_technician",
		},
		{
			"fieldname": "sl_pm_visit_col",
			"fieldtype": "Column Break",
			"insert_after": "spares_used",
		},
		{
			"fieldname": "findings_and_remarks",
			"label": "Findings and Remarks",
			"fieldtype": "Long Text",
			"reqd": 1,
			"description": '"All OK" must still be typed — cannot be blank',
			"insert_after": "sl_pm_visit_col",
		},
		{
			"fieldname": "customer_signature",
			"label": "Customer Signature",
			"fieldtype": "Signature",
			"reqd": 1,
			"description": "Captured by touch/finger on the technician's phone — Submit is blocked without it",
			"insert_after": "findings_and_remarks",
		},
		{
			"fieldname": "chargeable_visit",
			"label": "Chargeable Visit",
			"fieldtype": "Check",
			"description": "Ticked if this visit is billable to the developer",
			"insert_after": "customer_signature",
		},
		{
			"fieldname": "quarter",
			"label": "Quarter",
			"fieldtype": "Select",
			"options": "\nQ1\nQ2\nQ3\nQ4",
			"description": "Auto-fills from the visit date",
			"insert_after": "chargeable_visit",
		},
		{
			"fieldname": "pm_month",
			"label": "PM Month",
			"fieldtype": "Select",
			"options": "\nMonth 1\nMonth 2\nMonth 3",
			"insert_after": "quarter",
		},
		# Sales Order + its read-only Job Number / Job Name — supersedes the
		# generic job_id field setup/job_id.py would otherwise create here.
		{
			"fieldname": "job_id",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"description": "Links the visit to the specific deployment",
			"insert_after": "pm_month",
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
	]
}


def setup_maintenance_visit_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
