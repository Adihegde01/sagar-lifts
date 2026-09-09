"""Sales Order customisation for Sagar Lifts — Construction Lift Order.

All business fields live directly on the standard Sales Order (no new doctype).
Shipped as Custom Fields + Property Setters so every site gets them on
install / migrate.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Sales Order": [
		# --- Lift Order tab ---------------------------------------------------
		{
			"fieldname": "sl_lift_order_tab",
			"label": "Lift Order",
			"fieldtype": "Tab Break",
			"insert_after": "party_account_currency",
		},
		{
			"fieldname": "sl_lift_details_section",
			"label": "Lift Details",
			"fieldtype": "Section Break",
			"insert_after": "sl_lift_order_tab",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"read_only": 0,
			"description": "Defaults to the auto-assigned Job Number — the identifier that travels with this deployment for its whole life",
			"insert_after": "sl_lift_details_section",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"reqd": 1,
			"description": 'e.g. "ABC Constructions — Bangalore — SC200/200"',
			"insert_after": "job_number",
		},
		{
			"fieldname": "lift_type",
			"label": "Lift Type",
			"fieldtype": "Select",
			"options": "Construction\nPermanent\nRe-erection\nDismantling",
			"reqd": 1,
			"insert_after": "job_name",
		},
		{
			"fieldname": "lift_model",
			"label": "Lift Model",
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 1,
			"description": "Lift-model items only",
			"insert_after": "lift_type",
		},
		{
			"fieldname": "lift_height",
			"label": "Lift Height (m)",
			"fieldtype": "Float",
			"reqd": 1,
			"insert_after": "lift_model",
		},
		{
			"fieldname": "sl_lift_details_col",
			"fieldtype": "Column Break",
			"insert_after": "lift_height",
		},
		{
			"fieldname": "capacity_kg",
			"label": "Capacity (kg)",
			"fieldtype": "Float",
			"reqd": 1,
			"insert_after": "sl_lift_details_col",
		},
		{
			"fieldname": "cabin_size",
			"label": "Cabin Size",
			"fieldtype": "Data",
			"reqd": 1,
			"description": "e.g. 1.5m × 1.3m",
			"insert_after": "capacity_kg",
		},
		{
			"fieldname": "jumping_rate",
			"label": "Jumping Rate (₹)",
			"fieldtype": "Currency",
			"reqd": 1,
			"description": "Per jump — enter 0 if not yet decided",
			"insert_after": "cabin_size",
		},
		{
			"fieldname": "free_maintenance_months",
			"label": "Free Maintenance Months",
			"fieldtype": "Int",
			"reqd": 1,
			"description": "0 means no free period",
			"insert_after": "jumping_rate",
		},
		{
			"fieldname": "collection_lead",
			"label": "Collection Lead",
			"fieldtype": "Link",
			"options": "User",
			"reqd": 1,
			"description": "Auto-filled from developer — can be overridden",
			"insert_after": "free_maintenance_months",
		},
		# --- Payment Milestones --------------------------------------------------
		{
			"fieldname": "sl_milestones_section",
			"label": "Payment Milestones",
			"fieldtype": "Section Break",
			"insert_after": "collection_lead",
		},
		{
			"fieldname": "milestone_1_name",
			"label": "Milestone 1 Name",
			"fieldtype": "Data",
			"reqd": 1,
			"description": "e.g. Advance",
			"insert_after": "sl_milestones_section",
		},
		{
			"fieldname": "milestone_1_percent",
			"label": "Milestone 1 %",
			"fieldtype": "Percent",
			"reqd": 1,
			"insert_after": "milestone_1_name",
		},
		{
			"fieldname": "milestone_2_name",
			"label": "Milestone 2 Name",
			"fieldtype": "Data",
			"description": "e.g. On Delivery",
			"insert_after": "milestone_1_percent",
		},
		{
			"fieldname": "milestone_2_percent",
			"label": "Milestone 2 %",
			"fieldtype": "Percent",
			"insert_after": "milestone_2_name",
		},
		{
			"fieldname": "sl_milestones_col",
			"fieldtype": "Column Break",
			"insert_after": "milestone_2_percent",
		},
		{
			"fieldname": "milestone_3_name",
			"label": "Milestone 3 Name",
			"fieldtype": "Data",
			"description": "e.g. On Erection",
			"insert_after": "sl_milestones_col",
		},
		{
			"fieldname": "milestone_3_percent",
			"label": "Milestone 3 %",
			"fieldtype": "Percent",
			"insert_after": "milestone_3_name",
		},
		{
			"fieldname": "milestone_4_name",
			"label": "Milestone 4 Name",
			"fieldtype": "Data",
			"description": "e.g. On Handover",
			"insert_after": "milestone_3_percent",
		},
		{
			"fieldname": "milestone_4_percent",
			"label": "Milestone 4 %",
			"fieldtype": "Percent",
			"insert_after": "milestone_4_name",
		},
		{
			"fieldname": "milestone_percent_total",
			"label": "Milestone % Total",
			"fieldtype": "Float",
			"read_only": 1,
			"description": "Auto-calculated — must equal 100",
			"insert_after": "milestone_4_percent",
		},
		# --- Deployment --------------------------------------------------------
		{
			"fieldname": "sl_deployment_section",
			"label": "Deployment",
			"fieldtype": "Section Break",
			"insert_after": "milestone_percent_total",
		},
		{
			"fieldname": "deployment_status",
			"label": "Deployment Status",
			"fieldtype": "Select",
			"options": "\nActive\nDispatched\nInstallation\nHanded Over\nAMC\nDismantled",
			"description": "Workflow state field",
			"insert_after": "sl_deployment_section",
		},
		{
			"fieldname": "advance_received",
			"label": "Advance Received",
			"fieldtype": "Check",
			"description": "Ticked when advance payment confirmed — unlocks dispatch",
			"insert_after": "deployment_status",
		},
		{
			"fieldname": "dispatch_override_approved",
			"label": "Dispatch Override Approved",
			"fieldtype": "Check",
			"permlevel": 1,
			"description": "Admin/Management ticks if dispatch is needed without advance",
			"insert_after": "advance_received",
		},
		{
			"fieldname": "post_dismantle_instruction",
			"label": "Post Dismantle Instruction",
			"fieldtype": "Select",
			"options": "\nRe-deploy\nDeveloper Keeps\nDecision Pending",
			"insert_after": "dispatch_override_approved",
		},
		{
			"fieldname": "sl_deployment_col",
			"fieldtype": "Column Break",
			"insert_after": "post_dismantle_instruction",
		},
		{
			"fieldname": "handover_date",
			"label": "Handover Date",
			"fieldtype": "Date",
			"description": "Filled by Manufacturing when confirming handover",
			"insert_after": "sl_deployment_col",
		},
		{
			"fieldname": "amc_start_date",
			"label": "AMC Start Date",
			"fieldtype": "Date",
			"description": "Auto-filled at handover: Handover Date + Free Maintenance Months",
			"insert_after": "handover_date",
		},
		# --- Fleet & Billing -------------------------------------------------
		{
			"fieldname": "sl_fleet_section",
			"label": "Fleet & Billing",
			"fieldtype": "Section Break",
			"insert_after": "amc_start_date",
		},
		{
			"fieldname": "lift_status",
			"label": "Lift Status",
			"fieldtype": "Data",
			"description": "e.g. Available for Re-erection, Retired from Sagar Fleet",
			"insert_after": "sl_fleet_section",
		},
		{
			"fieldname": "outstanding_flag",
			"label": "Outstanding Flag",
			"fieldtype": "Check",
			"description": "Manually ticked when a PI for this developer is overdue",
			"insert_after": "lift_status",
		},
		{
			"fieldname": "sl_fleet_col",
			"fieldtype": "Column Break",
			"insert_after": "outstanding_flag",
		},
		{
			"fieldname": "contractor_labour_bills_percent",
			"label": "Contractor Labour Bills %",
			"fieldtype": "Float",
			"description": "Running total across all bills — cannot exceed 100%",
			"insert_after": "sl_fleet_col",
		},
		{
			"fieldname": "monthly_amc_rate",
			"label": "Monthly AMC Rate (₹)",
			"fieldtype": "Currency",
			"description": "Set at order creation for AMC orders — AMC lifecycle is tracked on a Contract",
			"insert_after": "contractor_labour_bills_percent",
		},
	]
}

def setup_sales_order_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	# Naming series stays stock (SAL-ORD-.YYYY.-); drop any series overrides an
	# earlier version of this setup may have applied.
	frappe.db.delete(
		"Property Setter",
		{"doc_type": "Sales Order", "field_name": "naming_series", "property": ["in", ("options", "default")]},
	)
	frappe.clear_cache(doctype="Sales Order")
