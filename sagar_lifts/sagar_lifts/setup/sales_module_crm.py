"""Sagar Lifts Sales Module — CRM Lead/Opportunity customisation.

Adds a "Sagar Lifts Sales" tab to the standard (classic ERPNext) Lead and
Opportunity doctypes, per the Sales Module Guide Section 4.3/4.4. Fields are
inserted after "notes" so the new tab lands right before the native
Dashboard tab. Role structure here follows the flat SL Sales/SL Admin roles
already in use (roles.py), not the guide's literal 5-tier SL
Scouter/Caller/Supervisor/Senior/Admin breakdown.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Lead": [
		{
			"fieldname": "sl_sales_tab",
			"label": "Sagar Lifts Sales",
			"fieldtype": "Tab Break",
			"insert_after": "notes",
		},
		# --- Lead Tracking ------------------------------------------------
		{
			"fieldname": "sl_lead_tracking_section",
			"label": "Lead Tracking",
			"fieldtype": "Section Break",
			"insert_after": "sl_sales_tab",
		},
		{
			"fieldname": "scout_report_reference",
			"label": "Scout Report Reference",
			"fieldtype": "Link",
			"options": "SL Scout Report",
			"insert_after": "sl_lead_tracking_section",
		},
		{
			"fieldname": "assigned_caller",
			"label": "Assigned Caller",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "scout_report_reference",
		},
		{
			"fieldname": "sl_lead_tracking_col",
			"fieldtype": "Column Break",
			"insert_after": "assigned_caller",
		},
		{
			"fieldname": "assigned_senior",
			"label": "Assigned Senior",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "sl_lead_tracking_col",
		},
		{
			"fieldname": "lead_quality",
			"label": "Lead Quality",
			"fieldtype": "Select",
			"options": "\nA Hot\nB Good\nC Average\nD Weak",
			"insert_after": "assigned_senior",
		},
		# --- Site & Requirement ---------------------------------------------
		{
			"fieldname": "sl_site_requirement_section",
			"label": "Site and Requirement",
			"fieldtype": "Section Break",
			"insert_after": "lead_quality",
		},
		{
			"fieldname": "site_name",
			"label": "Site Name",
			"fieldtype": "Data",
			"insert_after": "sl_site_requirement_section",
		},
		{
			"fieldname": "site_city",
			"label": "Site City",
			"fieldtype": "Data",
			"insert_after": "site_name",
		},
		{
			"fieldname": "proposed_building_height_floors",
			"label": "Proposed Building Height (floors)",
			"fieldtype": "Int",
			"insert_after": "site_city",
		},
		{
			"fieldname": "estimated_lifts_required",
			"label": "Estimated Lifts Required",
			"fieldtype": "Int",
			"insert_after": "proposed_building_height_floors",
		},
		{
			"fieldname": "sl_site_requirement_col",
			"fieldtype": "Column Break",
			"insert_after": "estimated_lifts_required",
		},
		{
			"fieldname": "estimated_height_m",
			"label": "Estimated Height (m)",
			"fieldtype": "Float",
			"insert_after": "sl_site_requirement_col",
		},
		{
			"fieldname": "estimated_contract_value",
			"label": "Estimated Contract Value (₹)",
			"fieldtype": "Currency",
			"insert_after": "estimated_height_m",
		},
		{
			"fieldname": "competitor_at_site",
			"label": "Competitor at Site",
			"fieldtype": "Check",
			"insert_after": "estimated_contract_value",
		},
		{
			"fieldname": "competitor_name",
			"label": "Competitor Name",
			"fieldtype": "Data",
			"depends_on": "competitor_at_site",
			"insert_after": "competitor_at_site",
		},
		# --- Follow Up --------------------------------------------------------
		{
			"fieldname": "sl_follow_up_section",
			"label": "Follow Up",
			"fieldtype": "Section Break",
			"insert_after": "competitor_name",
		},
		{
			"fieldname": "first_call_date",
			"label": "First Call Date",
			"fieldtype": "Date",
			"insert_after": "sl_follow_up_section",
		},
		{
			"fieldname": "last_follow_up_date",
			"label": "Last Follow Up Date",
			"fieldtype": "Date",
			"insert_after": "first_call_date",
		},
		{
			"fieldname": "next_follow_up_date",
			"label": "Next Follow Up Date",
			"fieldtype": "Date",
			"insert_after": "last_follow_up_date",
		},
		{
			"fieldname": "follow_up_count",
			"label": "Follow Up Count",
			"fieldtype": "Int",
			"insert_after": "next_follow_up_date",
		},
		{
			"fieldname": "sl_follow_up_col",
			"fieldtype": "Column Break",
			"insert_after": "follow_up_count",
		},
		{
			"fieldname": "meeting_scheduled",
			"label": "Meeting Scheduled",
			"fieldtype": "Check",
			"insert_after": "sl_follow_up_col",
		},
		{
			"fieldname": "meeting_date",
			"label": "Meeting Date",
			"fieldtype": "Date",
			"depends_on": "meeting_scheduled",
			"insert_after": "meeting_scheduled",
		},
		{
			"fieldname": "meeting_outcome",
			"label": "Meeting Outcome",
			"fieldtype": "Select",
			"options": "\nVery Positive\nPositive\nNeutral\nNeeds Follow Up\nNot Interested\nLost",
			"insert_after": "meeting_date",
		},
		{
			"fieldname": "second_meeting_required",
			"label": "Second Meeting Required",
			"fieldtype": "Check",
			"insert_after": "meeting_outcome",
		},
		# --- Admin Processing ---------------------------------------------------
		{
			"fieldname": "sl_lead_admin_section",
			"label": "Admin Processing",
			"fieldtype": "Section Break",
			"insert_after": "second_meeting_required",
		},
		{
			"fieldname": "admin_to_attend_closure",
			"label": "Admin to Attend Closure",
			"fieldtype": "Check",
			"insert_after": "sl_lead_admin_section",
		},
		{
			"fieldname": "quotation_request_submitted",
			"label": "Quotation Request Submitted",
			"fieldtype": "Check",
			"insert_after": "admin_to_attend_closure",
		},
		{
			"fieldname": "quotation_number",
			"label": "Quotation Number",
			"fieldtype": "Data",
			"insert_after": "quotation_request_submitted",
		},
		{
			"fieldname": "sl_lead_admin_col",
			"fieldtype": "Column Break",
			"insert_after": "quotation_number",
		},
		{
			"fieldname": "caller_remarks",
			"label": "Caller Remarks",
			"fieldtype": "Small Text",
			"insert_after": "sl_lead_admin_col",
		},
		{
			"fieldname": "senior_remarks",
			"label": "Senior Remarks",
			"fieldtype": "Small Text",
			"insert_after": "caller_remarks",
		},
	],
	"Opportunity": [
		{
			"fieldname": "sl_sales_tab",
			"label": "Sagar Lifts Sales",
			"fieldtype": "Tab Break",
			"insert_after": "notes",
		},
		# --- Quotation & Site -----------------------------------------------
		{
			"fieldname": "sl_quotation_site_section",
			"label": "Quotation and Site",
			"fieldtype": "Section Break",
			"insert_after": "sl_sales_tab",
		},
		{
			"fieldname": "quotation_request_reference",
			"label": "Quotation Request Reference",
			"fieldtype": "Link",
			"options": "SL Quotation Request",
			"insert_after": "sl_quotation_site_section",
		},
		{
			"fieldname": "quotation_reference",
			"label": "Quotation Reference",
			"fieldtype": "Link",
			"options": "Quotation",
			"insert_after": "quotation_request_reference",
		},
		{
			"fieldname": "site_name",
			"label": "Site Name",
			"fieldtype": "Data",
			"insert_after": "quotation_reference",
		},
		{
			"fieldname": "lift_type",
			"label": "Lift Type",
			"fieldtype": "Select",
			"options": "\nConstruction\nPermanent\nRe-erection\nAMC Only",
			"insert_after": "site_name",
		},
		{
			"fieldname": "sl_quotation_site_col",
			"fieldtype": "Column Break",
			"insert_after": "lift_type",
		},
		{
			"fieldname": "number_of_lifts",
			"label": "Number of Lifts",
			"fieldtype": "Int",
			"insert_after": "sl_quotation_site_col",
		},
		{
			"fieldname": "estimated_height_m",
			"label": "Estimated Height (m)",
			"fieldtype": "Float",
			"insert_after": "number_of_lifts",
		},
		{
			"fieldname": "estimated_contract_value",
			"label": "Estimated Contract Value (₹)",
			"fieldtype": "Currency",
			"insert_after": "estimated_height_m",
		},
		# --- Closure ------------------------------------------------------------
		{
			"fieldname": "sl_closure_section",
			"label": "Closure",
			"fieldtype": "Section Break",
			"insert_after": "estimated_contract_value",
		},
		{
			"fieldname": "closure_meeting_done",
			"label": "Closure Meeting Done",
			"fieldtype": "Check",
			"insert_after": "sl_closure_section",
		},
		{
			"fieldname": "closure_meeting_date",
			"label": "Closure Meeting Date",
			"fieldtype": "Date",
			"depends_on": "closure_meeting_done",
			"insert_after": "closure_meeting_done",
		},
		{
			"fieldname": "closure_meeting_attendees",
			"label": "Closure Meeting Attendees",
			"fieldtype": "Small Text",
			"insert_after": "closure_meeting_date",
		},
		{
			"fieldname": "admin_attended_closure",
			"label": "Admin Attended Closure",
			"fieldtype": "Check",
			"insert_after": "closure_meeting_attendees",
		},
		{
			"fieldname": "sl_closure_col",
			"fieldtype": "Column Break",
			"insert_after": "admin_attended_closure",
		},
		{
			"fieldname": "order_confirmed",
			"label": "Order Confirmed",
			"fieldtype": "Check",
			"insert_after": "sl_closure_col",
		},
		{
			"fieldname": "sales_order_number",
			"label": "Sales Order Number",
			"fieldtype": "Link",
			"options": "Sales Order",
			"insert_after": "order_confirmed",
		},
		{
			"fieldname": "order_confirmed_date",
			"label": "Order Confirmed Date",
			"fieldtype": "Date",
			"depends_on": "order_confirmed",
			"insert_after": "sales_order_number",
		},
		# --- Team Involvement -----------------------------------------------
		{
			"fieldname": "sl_team_involvement_section",
			"label": "Team Involvement",
			"fieldtype": "Section Break",
			"insert_after": "order_confirmed_date",
		},
		{
			"fieldname": "scouter_involved",
			"label": "Scouter Involved",
			"fieldtype": "Check",
			"insert_after": "sl_team_involvement_section",
		},
		{
			"fieldname": "scouter_name",
			"label": "Scouter Name",
			"fieldtype": "Link",
			"options": "User",
			"depends_on": "scouter_involved",
			"insert_after": "scouter_involved",
		},
		{
			"fieldname": "caller_involved",
			"label": "Caller Involved",
			"fieldtype": "Check",
			"insert_after": "scouter_name",
		},
		{
			"fieldname": "caller_name",
			"label": "Caller Name",
			"fieldtype": "Link",
			"options": "User",
			"depends_on": "caller_involved",
			"insert_after": "caller_involved",
		},
		{
			"fieldname": "sl_team_involvement_col",
			"fieldtype": "Column Break",
			"insert_after": "caller_name",
		},
		{
			"fieldname": "senior_involved",
			"label": "Senior Involved",
			"fieldtype": "Check",
			"insert_after": "sl_team_involvement_col",
		},
		{
			"fieldname": "senior_name",
			"label": "Senior Name",
			"fieldtype": "Link",
			"options": "User",
			"depends_on": "senior_involved",
			"insert_after": "senior_involved",
		},
		{
			"fieldname": "admin_involved",
			"label": "Admin Involved",
			"fieldtype": "Check",
			"insert_after": "senior_name",
		},
		# --- Incentive & Lost Tracking -----------------------------------------
		{
			"fieldname": "sl_incentive_lost_section",
			"label": "Incentive and Lost Tracking",
			"fieldtype": "Section Break",
			"insert_after": "admin_involved",
		},
		{
			"fieldname": "incentive_record_created",
			"label": "Incentive Record Created",
			"fieldtype": "Check",
			"insert_after": "sl_incentive_lost_section",
		},
		{
			"fieldname": "incentive_record_number",
			"label": "Incentive Record Number",
			"fieldtype": "Data",
			"insert_after": "incentive_record_created",
		},
		{
			"fieldname": "sl_incentive_lost_col",
			"fieldtype": "Column Break",
			"insert_after": "incentive_record_number",
		},
		{
			"fieldname": "lost_reason",
			"label": "Lost Reason",
			"fieldtype": "Select",
			"options": "\nPrice Too High\nCompetitor Preferred\nProject Delayed\nProject Cancelled\nNo Response\nBudget Cut",
			"insert_after": "sl_incentive_lost_col",
		},
		{
			"fieldname": "lost_to_competitor",
			"label": "Lost to Competitor",
			"fieldtype": "Data",
			"depends_on": "eval:doc.lost_reason==\"Competitor Preferred\"",
			"insert_after": "lost_reason",
		},
	],
	# Sales guide 7.3: the Quotation links back to the request it answers;
	# submitting it marks the request Quotation Generated (doc_events).
	"Quotation": [
		{
			"fieldname": "quotation_request",
			"label": "Quotation Request",
			"fieldtype": "Link",
			"options": "SL Quotation Request",
			"insert_after": "party_name",
		},
	],
}


def setup_sales_module_crm_fields():
	import frappe

	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Lead")
	frappe.clear_cache(doctype="Opportunity")
	frappe.clear_cache(doctype="Quotation")
