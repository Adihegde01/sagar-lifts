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
			# Right after the Details tab, before Address & Contact.
			"insert_after": "pricing_rules",
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
			"allow_on_submit": 1,
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
			"allow_on_submit": 1,
			"description": "Per jump — enter 0 if not yet decided. Admin can fill this in later if it was 0 at order creation",
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
			"fetch_from": "customer.collection_lead",
			"fetch_if_empty": 1,
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
			"allow_on_submit": 1,
			"description": "Workflow state field",
			"insert_after": "sl_deployment_section",
		},
		{
			"fieldname": "advance_received",
			"label": "Advance Received",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "Ticked when advance payment confirmed — unlocks dispatch",
			"insert_after": "deployment_status",
		},
		{
			"fieldname": "dispatch_override_approved",
			"label": "Dispatch Override Approved",
			"fieldtype": "Check",
			"permlevel": 1,
			"allow_on_submit": 1,
			"description": "Admin/Management ticks if dispatch is needed without advance",
			"insert_after": "advance_received",
		},
		{
			"fieldname": "post_dismantle_instruction",
			"label": "Post Dismantle Instruction",
			"fieldtype": "Select",
			"options": "\nRe-deploy\nDeveloper Keeps\nDecision Pending",
			"allow_on_submit": 1,
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
			"allow_on_submit": 1,
			"description": "Filled by Manufacturing when confirming handover",
			"insert_after": "sl_deployment_col",
		},
		{
			"fieldname": "amc_start_date",
			"label": "AMC Start Date",
			"fieldtype": "Date",
			"allow_on_submit": 1,
			"description": "Auto-filled at handover: Handover Date + Free Maintenance Months",
			"insert_after": "handover_date",
		},
		# --- Handover Checklist --------------------------------------------
		# The guide's real handover gate (Section 4.1 MUST list) — replaces
		# the earlier placeholder of just requiring Handover Date to be filled.
		{
			"fieldname": "sl_handover_checklist_section",
			"label": "Handover Checklist",
			"fieldtype": "Section Break",
			"insert_after": "amc_start_date",
		},
		{
			"fieldname": "erection_completion_confirmed",
			"label": "Erection Completion Confirmed",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "Confirmed by site supervisor, by way of handover paper",
			"insert_after": "sl_handover_checklist_section",
		},
		{
			"fieldname": "third_party_inspection_done",
			"label": "Third Party Inspection Done",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "If applicable for this order type",
			"insert_after": "erection_completion_confirmed",
		},
		{
			"fieldname": "signed_handover_paper_received",
			"label": "Signed Handover Paper Received",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "Signed by: Contractor, Inspection technician, Client representative",
			"insert_after": "third_party_inspection_done",
		},
		{
			"fieldname": "sl_handover_checklist_col",
			"fieldtype": "Column Break",
			"insert_after": "signed_handover_paper_received",
		},
		{
			"fieldname": "on_delivery_payment_cleared",
			"label": "On Delivery Payment Cleared",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "Payment up to and including the On Delivery milestone must be fully received",
			"insert_after": "sl_handover_checklist_col",
		},
		{
			"fieldname": "handover_payment_override_approved",
			"label": "Handover Payment Override Approved",
			"fieldtype": "Check",
			"permlevel": 1,
			"allow_on_submit": 1,
			"description": "Admin/Management ticks if handover is needed without full On Delivery payment",
			"insert_after": "on_delivery_payment_cleared",
		},
		# --- Dismantling Checklist ---------------------------------------------
		# Required only at Deployment Status = Dismantled; wired into the
		# AMC -> Dismantled workflow transition condition.
		{
			"fieldname": "sl_dismantling_checklist_section",
			"label": "Dismantling Checklist",
			"fieldtype": "Section Break",
			"insert_after": "handover_payment_override_approved",
		},
		{
			"fieldname": "dismantle_instruction_received",
			"label": "Dismantle Instruction Received",
			"fieldtype": "Check",
			"mandatory_depends_on": 'eval:doc.deployment_status=="Dismantled"',
			"allow_on_submit": 1,
			"description": "The formal developer instruction, logged before anything else proceeds",
			"insert_after": "sl_dismantling_checklist_section",
		},
		{
			"fieldname": "all_amc_billing_raised",
			"label": "All AMC Billing Raised",
			"fieldtype": "Check",
			"mandatory_depends_on": 'eval:doc.deployment_status=="Dismantled"',
			"allow_on_submit": 1,
			"description": "Every unbilled AMC amount, even a part-quarter, must have a PI raised",
			"insert_after": "dismantle_instruction_received",
		},
		{
			"fieldname": "sl_dismantling_checklist_col",
			"fieldtype": "Column Break",
			"insert_after": "all_amc_billing_raised",
		},
		{
			"fieldname": "final_pm_visit_logged",
			"label": "Final PM Visit Logged",
			"fieldtype": "Check",
			"mandatory_depends_on": 'eval:doc.deployment_status=="Dismantled"',
			"allow_on_submit": 1,
			"description": "Linked to the last Maintenance Visit on this lift",
			"insert_after": "sl_dismantling_checklist_col",
		},
		{
			"fieldname": "dismantling_billing_trigger_created",
			"label": "Dismantling Billing Trigger Created",
			"fieldtype": "Check",
			"mandatory_depends_on": 'eval:doc.deployment_status=="Dismantled"',
			"allow_on_submit": 1,
			"insert_after": "final_pm_visit_logged",
		},
		# --- Fleet & Billing -------------------------------------------------
		{
			"fieldname": "sl_fleet_section",
			"label": "Fleet & Billing",
			"fieldtype": "Section Break",
			"insert_after": "dismantling_billing_trigger_created",
		},
		{
			"fieldname": "lift_status",
			"label": "Lift Status",
			"fieldtype": "Data",
			"allow_on_submit": 1,
			"description": "e.g. Available for Re-erection, Retired from Sagar Fleet",
			"insert_after": "sl_fleet_section",
		},
		{
			"fieldname": "outstanding_flag",
			"label": "Outstanding Flag",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"description": "Manually ticked when a PI for this developer is overdue",
			"insert_after": "lift_status",
		},
		{
			"fieldname": "pm_visit_overdue",
			"label": "PM Visit Overdue",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"read_only": 1,
			"description": "Auto-set if no PM visit is logged for this lift by the 25th of the month",
			"insert_after": "outstanding_flag",
		},
		{
			"fieldname": "sl_fleet_col",
			"fieldtype": "Column Break",
			"insert_after": "pm_visit_overdue",
		},
		{
			"fieldname": "contractor_labour_bills_percent",
			"label": "Contractor Labour Bills %",
			"fieldtype": "Float",
			"allow_on_submit": 1,
			"description": "Running total across all bills — cannot exceed 100%",
			"insert_after": "sl_fleet_col",
		},
		{
			"fieldname": "monthly_amc_rate",
			"label": "Monthly AMC Rate (₹)",
			"fieldtype": "Currency",
			"allow_on_submit": 1,
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
