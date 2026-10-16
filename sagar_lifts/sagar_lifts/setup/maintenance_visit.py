"""Maintenance Visit — PM Visit.

Covers PM, Breakdown and Inspection visits with the same mandatory fields.
This is the one doctype SL Technician touches, logged from the mobile app on
their own assigned visits only. Visit Photos/Documents use the standard
Attachments panel — no custom field needed for that.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

CUSTOM_FIELDS = {
	"Maintenance Visit": [
		# --- Visit Information ------------------------------------------------
		# Visit Date / Visit Time In are the native Maintenance Date / Time
		# fields just above this section.
		{
			"fieldname": "sl_visit_info_section",
			"label": "Visit Information",
			"fieldtype": "Section Break",
			"insert_after": "mntc_time",
		},
		{
			"fieldname": "visit_type",
			"label": "Visit Type",
			"fieldtype": "Select",
			"options": "Preventive Maintenance\nBreakdown\nInspection\nWarranty Visit\nPost Repair Inspection",
			"reqd": 1,
			"description": "The Technician picks this when logging a PM visit or a breakdown call",
			"insert_after": "sl_visit_info_section",
		},
		# Sales Order + its read-only Job Number / Job Name — supersedes the
		# generic job_id field setup/job_id.py would otherwise create here.
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"description": "Links the visit to the specific deployment",
			"insert_after": "visit_type",
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
			"fieldname": "developer_name",
			"label": "Developer Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.developer_name",
			"fetch_if_empty": 1,
			"insert_after": "job_name",
		},
		{
			"fieldname": "site_name",
			"label": "Site Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.site_name",
			"fetch_if_empty": 1,
			"insert_after": "developer_name",
		},
		{
			"fieldname": "sl_visit_info_col",
			"fieldtype": "Column Break",
			"insert_after": "site_name",
		},
		{
			"fieldname": "lift_model",
			"label": "Lift Model",
			"fieldtype": "Data",
			"fetch_from": "job_id.lift_model",
			"fetch_if_empty": 1,
			"insert_after": "sl_visit_info_col",
		},
		{
			"fieldname": "lift_serial_number",
			"label": "Lift Serial Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.lift_serial_number",
			"fetch_if_empty": 1,
			"insert_after": "lift_model",
		},
		{
			"fieldname": "current_floor_level",
			"label": "Current Floor Level",
			"fieldtype": "Int",
			"fetch_from": "job_id.current_floor_level",
			"fetch_if_empty": 1,
			"insert_after": "lift_serial_number",
		},
		{
			"fieldname": "visit_time_out",
			"label": "Visit Time Out",
			"fieldtype": "Time",
			"insert_after": "current_floor_level",
		},
		{
			"fieldname": "total_hours_on_site",
			"label": "Total Hours on Site",
			"fieldtype": "Float",
			"read_only": 1,
			"description": "Time Out − Maintenance Time, calculated on save",
			"insert_after": "visit_time_out",
		},
		{
			"fieldname": "sl_pm_visit_section",
			"label": "PM Visit",
			"fieldtype": "Section Break",
			"insert_after": "purposes",
		},
		{
			"fieldname": "senior_technician",
			"label": "Senior Technician",
			"fieldtype": "Link",
			"options": "User",
			"reqd": 1,
			"description": "Must be selected from the registered technician list",
			"insert_after": "sl_pm_visit_section",
		},
		# --- PM Schedule --------------------------------------------------------
		{
			"fieldname": "sl_pm_schedule_section",
			"label": "PM Schedule",
			"fieldtype": "Section Break",
			"insert_after": "senior_technician",
		},
		{
			"fieldname": "quarter",
			"label": "Quarter",
			"fieldtype": "Select",
			"options": "\nQ1\nQ2\nQ3\nQ4",
			"description": "Auto-fills from the visit date",
			"insert_after": "sl_pm_schedule_section",
		},
		{
			"fieldname": "pm_month",
			"label": "PM Month in Quarter",
			"fieldtype": "Select",
			"options": "\nMonth 1\nMonth 2\nMonth 3",
			"insert_after": "quarter",
		},
		{
			"fieldname": "sl_pm_schedule_col",
			"fieldtype": "Column Break",
			"insert_after": "pm_month",
		},
		{
			"fieldname": "scheduled_visit_date",
			"label": "Scheduled Visit Date",
			"fieldtype": "Date",
			"fetch_from": "maintenance_schedule_detail.scheduled_date",
			"fetch_if_empty": 1,
			"insert_after": "sl_pm_schedule_col",
		},
		{
			"fieldname": "variance_from_schedule_days",
			"label": "Variance from Schedule (days)",
			"fieldtype": "Int",
			"read_only": 1,
			"description": "Visit Date − Scheduled Visit Date; positive = late",
			"insert_after": "scheduled_visit_date",
		},
		{
			"fieldname": "amc_approval_received",
			"label": "AMC Approval Received",
			"fieldtype": "Check",
			"insert_after": "variance_from_schedule_days",
		},
		# --- Findings & Work Done ----------------------------------------------
		{
			"fieldname": "sl_findings_section",
			"label": "Findings and Work Done",
			"fieldtype": "Section Break",
			"insert_after": "amc_approval_received",
		},
		{
			"fieldname": "findings_and_remarks",
			"label": "Findings and Observations",
			"fieldtype": "Long Text",
			"reqd": 1,
			"description": '"All OK" must still be typed — cannot be blank',
			"insert_after": "sl_findings_section",
		},
		{
			"fieldname": "work_done_details",
			"label": "Work Done Details",
			"fieldtype": "Text",
			"reqd": 0,
			# Required on drafts only, so records submitted before this field
			# existed can still be updated (workflow moves, after-submit edits).
			"mandatory_depends_on": "eval:doc.docstatus==0",
			"insert_after": "findings_and_remarks",
		},
		{
			"fieldname": "pending_work",
			"label": "Pending Work",
			"fieldtype": "Small Text",
			"insert_after": "work_done_details",
		},
		{
			"fieldname": "sl_findings_col",
			"fieldtype": "Column Break",
			"insert_after": "pending_work",
		},
		{
			"fieldname": "follow_up_required",
			"label": "Follow Up Required",
			"fieldtype": "Check",
			"insert_after": "sl_findings_col",
		},
		{
			"fieldname": "follow_up_details",
			"label": "Follow Up Details",
			"fieldtype": "Small Text",
			"depends_on": "follow_up_required",
			"insert_after": "follow_up_required",
		},
		{
			"fieldname": "next_visit_recommendations",
			"label": "Next Visit Recommendations",
			"fieldtype": "Small Text",
			"insert_after": "follow_up_details",
		},
	]
}

# --- Spares & Materials ---------------------------------------------------------
SPARE_PART_ROWS = 3
SPARE_SOURCES = "\nFrom Store\nPurchased Locally\nWarranty Replacement"
_SPARES_SHOWN = 'eval:doc.spares_used=="Spares Used"'


def _spares_fields():
	fields = [
		{
			"fieldname": "sl_spares_section",
			"label": "Spares and Materials",
			"fieldtype": "Section Break",
			"insert_after": "next_visit_recommendations",
		},
		{
			"fieldname": "spares_used",
			"label": "Spares Used",
			"fieldtype": "Select",
			"options": "No Spares Used\nSpares Used",
			"reqd": 1,
		},
	]
	for n in range(1, SPARE_PART_ROWS + 1):
		fields += [
			{"fieldname": f"sl_spare_part_{n}_col", "fieldtype": "Column Break"},
			{"fieldname": f"spare_part_{n}_name", "label": f"Spare Part {n} Name", "fieldtype": "Data", "depends_on": _SPARES_SHOWN},
			{"fieldname": f"spare_part_{n}_qty", "label": f"Spare Part {n} Qty", "fieldtype": "Float", "depends_on": _SPARES_SHOWN},
			{
				"fieldname": f"spare_part_{n}_source",
				"label": f"Spare Part {n} Source",
				"fieldtype": "Select",
				"options": SPARE_SOURCES,
				"depends_on": _SPARES_SHOWN,
			},
		]
	fields += [
		{"fieldname": "sl_spares_totals_section", "fieldtype": "Section Break", "depends_on": _SPARES_SHOWN},
		{"fieldname": "additional_spares_details", "label": "Additional Spares Details", "fieldtype": "Small Text"},
		{"fieldname": "sl_spares_totals_col", "fieldtype": "Column Break"},
		{"fieldname": "total_spares_cost", "label": "Total Spares Cost (₹)", "fieldtype": "Currency"},
		# --- Chargeable Visit ---
		{"fieldname": "sl_chargeable_section", "label": "Chargeable Visit", "fieldtype": "Section Break"},
		{
			"fieldname": "chargeable_visit",
			"label": "Chargeable Visit",
			"fieldtype": "Check",
			"description": "Ticked if this visit is billable to the developer",
		},
		{
			"fieldname": "chargeable_reason",
			"label": "Chargeable Reason",
			"fieldtype": "Select",
			"options": "\nOut of Scope\nDamage by Operator\nPost Warranty\nMisuse",
			"depends_on": "chargeable_visit",
		},
		{"fieldname": "sl_chargeable_col", "fieldtype": "Column Break"},
		{
			"fieldname": "chargeable_amount",
			"label": "Chargeable Amount (₹)",
			"fieldtype": "Currency",
			"depends_on": "chargeable_visit",
		},
		{
			"fieldname": "chargeable_approved_by",
			"label": "Chargeable Approved By",
			"fieldtype": "Link",
			"options": "User",
			"depends_on": "chargeable_visit",
		},
		# --- Customer Confirmation ---
		{"fieldname": "sl_customer_confirmation_section", "label": "Customer Confirmation", "fieldtype": "Section Break"},
		{
			"fieldname": "customer_signature",
			"label": "Customer Signature",
			"fieldtype": "Signature",
			"reqd": 1,
			"description": "Captured by touch/finger on the technician's phone — Submit is blocked without it",
		},
		{
			"fieldname": "customer_signature_received",
			"label": "Customer Signature Received",
			"fieldtype": "Check",
			"read_only": 1,
			"description": "Auto-ticked when the signature above is captured",
		},
		{"fieldname": "signed_by_at_site", "label": "Signed By at Site", "fieldtype": "Data"},
		{"fieldname": "signed_by_designation", "label": "Signed By Designation", "fieldtype": "Data"},
		{"fieldname": "sl_customer_confirmation_col", "fieldtype": "Column Break"},
		{
			# Not "customer_feedback" — that's Maintenance Visit's own free-text
			# field (hidden below); this one is the rating.
			"fieldname": "customer_feedback_rating",
			"label": "Customer Feedback",
			"fieldtype": "Select",
			"options": "\nSatisfied\nNeutral\nUnsatisfied",
		},
		{"fieldname": "customer_remarks", "label": "Customer Remarks", "fieldtype": "Small Text"},
		{"fieldname": "next_visit_due_date", "label": "Next Visit Due Date", "fieldtype": "Date"},
	]
	for prev, field in zip(fields, fields[1:]):
		field["insert_after"] = prev["fieldname"]
	return fields


CUSTOM_FIELDS["Maintenance Visit"] += _spares_fields()

# --- Breakdown Specific -----------------------------------------------------------
_BREAKDOWN_SHOWN = 'eval:doc.visit_type=="Breakdown"'
_BREAKDOWN_FIELDS = [
	{"fieldname": "sl_breakdown_section", "label": "Breakdown Specific", "fieldtype": "Section Break", "depends_on": _BREAKDOWN_SHOWN},
	{"fieldname": "breakdown_reported_by", "label": "Breakdown Reported By", "fieldtype": "Data"},
	{
		"fieldname": "breakdown_reported_via",
		"label": "Breakdown Reported Via",
		"fieldtype": "Select",
		"options": "\nPhone\nWhatsApp\nEmail\nIn Person",
	},
	{"fieldname": "breakdown_reported_date", "label": "Breakdown Reported Date", "fieldtype": "Date"},
	{"fieldname": "breakdown_reported_time", "label": "Breakdown Reported Time", "fieldtype": "Time"},
	{"fieldname": "technician_assigned_time", "label": "Technician Assigned Time", "fieldtype": "Time"},
	{"fieldname": "sl_breakdown_col_1", "fieldtype": "Column Break"},
	{"fieldname": "technician_reached_date", "label": "Technician Reached Date", "fieldtype": "Date"},
	{"fieldname": "technician_reached_time", "label": "Technician Reached Time", "fieldtype": "Time"},
	{"fieldname": "breakdown_resolved_date", "label": "Breakdown Resolved Date", "fieldtype": "Date"},
	{"fieldname": "breakdown_resolved_time", "label": "Breakdown Resolved Time", "fieldtype": "Time"},
	{
		"fieldname": "response_time_hours",
		"label": "Response Time (hours)",
		"fieldtype": "Float",
		"read_only": 1,
		"description": "Reported → Technician Reached, calculated on save",
	},
	{
		"fieldname": "resolution_time_hours",
		"label": "Resolution Time (hours)",
		"fieldtype": "Float",
		"read_only": 1,
		"description": "Reported → Resolved, calculated on save",
	},
	{"fieldname": "sl_breakdown_col_2", "fieldtype": "Column Break"},
	{"fieldname": "breakdown_cause", "label": "Breakdown Cause", "fieldtype": "Small Text"},
	{
		"fieldname": "breakdown_category",
		"label": "Breakdown Category",
		"fieldtype": "Select",
		"options": "\nElectrical\nMechanical\nOperator Error\nExternal Damage\nUnknown",
	},
	{"fieldname": "repeated_breakdown", "label": "Repeated Breakdown", "fieldtype": "Check"},
	{
		"fieldname": "repeated_breakdown_count",
		"label": "Repeated Breakdown Count",
		"fieldtype": "Int",
		"depends_on": "repeated_breakdown",
	},
]
_BREAKDOWN_FIELDS[0]["insert_after"] = "next_visit_due_date"
for _prev, _field in zip(_BREAKDOWN_FIELDS, _BREAKDOWN_FIELDS[1:]):
	_field["insert_after"] = _prev["fieldname"]
CUSTOM_FIELDS["Maintenance Visit"] += _BREAKDOWN_FIELDS

# --- Internal Notes ------------------------------------------------------------------
CUSTOM_FIELDS["Maintenance Visit"] += [
	{
		"fieldname": "sl_mv_internal_notes_section",
		"label": "Internal Notes",
		"fieldtype": "Section Break",
		"insert_after": "repeated_breakdown_count",
	},
	{
		"fieldname": "internal_technical_notes",
		"label": "Internal Technical Notes",
		"fieldtype": "Small Text",
		"insert_after": "sl_mv_internal_notes_section",
	},
	{
		"fieldname": "sl_mv_internal_notes_col",
		"fieldtype": "Column Break",
		"insert_after": "internal_technical_notes",
	},
	{
		"fieldname": "escalation_required",
		"label": "Escalation Required",
		"fieldtype": "Check",
		"insert_after": "sl_mv_internal_notes_col",
	},
	{
		"fieldname": "escalation_reason",
		"label": "Escalation Reason",
		"fieldtype": "Small Text",
		"depends_on": "escalation_required",
		"mandatory_depends_on": "escalation_required",
		"insert_after": "escalation_required",
	},
]


def _ensure_default_service_person():
	# Every visit's auto-added Purposes row (doc_events.maintenance_visit_add_purpose)
	# needs a Sales Person; technicians are Users, not Sales Persons.
	if frappe.db.exists("Sales Person", "Default Technician"):
		return
	root = frappe.db.get_value("Sales Person", {"is_group": 1, "parent_sales_person": ["in", ("", None)]})
	frappe.get_doc(
		{"doctype": "Sales Person", "sales_person_name": "Default Technician", "parent_sales_person": root}
	).insert(ignore_permissions=True)


def setup_maintenance_visit_customization():
	_ensure_default_service_person()
	# PM Visit's column break went away when Customer Signature moved out.
	frappe.db.delete("Custom Field", {"dt": "Maintenance Visit", "fieldname": "sl_pm_visit_col"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	# Superseded by Customer Feedback (rating) + Customer Remarks.
	make_property_setter("Maintenance Visit", "customer_feedback", "hidden", 1, "Check", validate_fields_for_doctype=False)
