"""Sales Module notifications (Sales Module Guide, Section 6).

The guide lists 26 triggers. Three adaptations from its literal wording:

  - #22-24 ("Every Monday"/"Every Friday") have no document to hang a
    Frappe Notification off of — Frappe's Notification doctype has no
    day-of-week event type. They're implemented as scheduler cron jobs
    instead, in sales_reminders.py (wired in hooks.scheduler_events).
  - #2 ("Scout Report Assigned to Caller") and #4 ("New Lead Assigned")
    are the same trigger (Lead, Assigned Caller changes) with overlapping
    recipients — kept as one notification (SL New Lead Assigned to
    Caller) instead of firing two emails for one action. The Scouter
    being CC'd is dropped: Lead has no scouter-user field to notify by
    (scouter identity lives on SL Scout Report, which Lead only links to
    by reference, not by a fetched user field).
  - Section 6.4's "Meeting ..." notifications are listed against CRM
    Opportunity, but Meeting Scheduled/Meeting Date/Meeting Outcome/
    Second Meeting Required are Lead fields per the guide's own Section
    4.3 field table (Opportunity's 4.4 table has no such fields) — they
    target Lead here, matching where the fields actually live.

Role mapping (this build uses the flat SL Sales/SL Admin/SL Management
roles already shipped in roles.py, not the guide's literal 5-tier
Scouter/Caller/Supervisor/Senior/Admin breakdown):
  - Scouter, Caller, Senior  -> SL Sales (role) or a specific
    assigned_caller/assigned_senior/scouter_name/caller_name/senior_name
    field where the guide names a specific person
  - Sales Supervisor          -> SL Admin (Admin already does "daily
    oversight" per the guide's own Section 1.1 role table)
  - Sales Admin                -> SL Admin
  - Management                 -> SL Management
"""

from frappe.email.doctype.notification.notification import create_notifications


def _role(role):
	return {"receiver_by_role": role}


def _field(fieldname):
	return {"receiver_by_document_field": fieldname}


BASE = {
	"channel": "Email",
	"send_system_notification": 1,
	"notification_type": "Alert",
	"condition_type": "Python",
}

NOTIFICATIONS = [
	# --- 6.1 Scouting ---------------------------------------------------------
	{
		**BASE,
		"name": "SL New Scout Report Submitted",
		"document_type": "SL Scout Report",
		"event": "Submit",
		"subject": "New Scout Report Submitted — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		# Covers guide #2 and #4 — see module docstring.
		**BASE,
		"name": "SL New Lead Assigned to Caller",
		"document_type": "Lead",
		"event": "Value Change",
		"value_changed": "assigned_caller",
		"condition": "doc.assigned_caller",
		"subject": "New Lead Assigned to You — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_caller")],
	},
	{
		**BASE,
		"name": "SL Weekly Scout Review Due",
		"document_type": "SL Scout Report",
		"event": "Days After",
		"date_changed": "visit_date",
		"days_in_advance": 7,
		"subject": "Weekly Scout Review Due — {{ doc.name }}",
		"recipients": [_role("SL Sales Supervisor")],
	},
	# --- 6.2 Lead and Calling -------------------------------------------------
	{
		**BASE,
		"name": "SL Follow Up Due Today",
		"document_type": "Lead",
		"event": "Days After",
		"date_changed": "next_follow_up_date",
		"days_in_advance": 0,
		"subject": "Follow Up Due Today — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_caller"), _role("SL Sales Supervisor")],
	},
	{
		**BASE,
		"name": "SL Follow Up Overdue",
		"document_type": "Lead",
		"event": "Days After",
		"date_changed": "next_follow_up_date",
		"days_in_advance": 2,
		"subject": "Follow Up OVERDUE — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_caller"), _role("SL Sales Supervisor")],
	},
	{
		**BASE,
		"name": "SL Lead Going Cold - 7 Days",
		"document_type": "Lead",
		"event": "Days After",
		"date_changed": "last_follow_up_date",
		"days_in_advance": 7,
		"subject": "Lead Going Cold — No Activity in 7 Days — {{ doc.lead_name or doc.name }}",
		"recipients": [_role("SL Sales Supervisor"), _role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Lead Going Cold - 14 Days",
		"document_type": "Lead",
		"event": "Days After",
		"date_changed": "last_follow_up_date",
		"days_in_advance": 14,
		"subject": "ESCALATION — Lead Cold 14 Days, May Be Lost — {{ doc.lead_name or doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin")],
	},
	# --- 6.3 Quotation ---------------------------------------------------------
	{
		**BASE,
		"name": "SL Quotation Request Submitted",
		"document_type": "SL Quotation Request",
		"event": "Submit",
		"subject": "Quotation Request Submitted — Generate Quotation Now — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Quotation Generated",
		"document_type": "Quotation",
		"event": "Submit",
		"subject": "Quotation Ready — Share With Developer — {{ doc.name }}",
		"recipients": [_role("SL Caller"), _role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Quotation Expiring in 3 Days",
		"document_type": "Quotation",
		"event": "Days Before",
		"date_changed": "valid_till",
		"days_in_advance": 3,
		"subject": "Quotation Expiring in 3 Days — Follow Up Urgently — {{ doc.name }}",
		"recipients": [_role("SL Caller"), _role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Quotation Expired - No Order",
		"document_type": "Quotation",
		"event": "Days After",
		"date_changed": "valid_till",
		"days_in_advance": 1,
		"condition": "doc.status not in ('Ordered', 'Partially Ordered')",
		"subject": "Quotation Expired Without Order — Review — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin"), _role("SL Sales Supervisor")],
	},
	# --- 6.4 Meeting (Lead fields — see module docstring) ----------------------
	{
		**BASE,
		"name": "SL Meeting Scheduled - Alert Senior",
		"document_type": "Lead",
		"event": "Value Change",
		"value_changed": "meeting_scheduled",
		"condition": "doc.meeting_scheduled",
		"subject": "Meeting Scheduled — Prepare — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_senior"), _role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Meeting Tomorrow Reminder",
		"document_type": "Lead",
		"event": "Days Before",
		"date_changed": "meeting_date",
		"days_in_advance": 1,
		"subject": "Meeting Tomorrow — Prepare — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_senior"), _field("assigned_caller")],
	},
	{
		**BASE,
		"name": "SL Meeting Done - Log Outcome",
		"document_type": "Lead",
		"event": "Days After",
		"date_changed": "meeting_date",
		"days_in_advance": 1,
		"condition": "not doc.meeting_outcome",
		"subject": "Please Log Meeting Outcome — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_senior")],
	},
	{
		**BASE,
		"name": "SL Admin Required for Closure",
		"document_type": "Lead",
		"event": "Value Change",
		"value_changed": "admin_to_attend_closure",
		"condition": "doc.admin_to_attend_closure",
		"subject": "Admin Needed for Closure Meeting — {{ doc.lead_name or doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin"), _role("SL Management")],
	},
	{
		**BASE,
		"name": "SL Second Meeting Required",
		"document_type": "Lead",
		"event": "Value Change",
		"value_changed": "second_meeting_required",
		"condition": "doc.second_meeting_required",
		"subject": "Second Meeting Required — Schedule It — {{ doc.lead_name or doc.name }}",
		"recipients": [_field("assigned_senior"), _role("SL Sales Supervisor")],
	},
	# --- 6.5 Order and Incentive -------------------------------------------
	{
		**BASE,
		"name": "SL Order Confirmed - Create Incentive",
		"document_type": "Sales Order",
		"event": "Submit",
		"subject": "Order Confirmed — Create Incentive Record — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin")],
	},
	{
		**BASE,
		"name": "SL Incentive Record Created",
		"document_type": "SL Incentive Record",
		"event": "New",
		"subject": "Your Incentive for Order {{ doc.sales_order }} Has Been Recorded",
		"recipients": [
			_field("scouter_name"),
			_field("caller_name"),
			_field("senior_name"),
			_field("admin_name"),
			_field("additional_member_1"),
		],
	},
	{
		**BASE,
		"name": "SL Incentive Approved",
		"document_type": "SL Incentive Record",
		"event": "Submit",
		"subject": "Incentive Approved — Payment Will Follow — {{ doc.name }}",
		"recipients": [
			_field("scouter_name"),
			_field("caller_name"),
			_field("senior_name"),
			_field("admin_name"),
			_field("additional_member_1"),
		],
	},
	{
		**BASE,
		"name": "SL Incentive Paid",
		"document_type": "SL Incentive Record",
		"event": "Value Change",
		"value_changed": "incentive_paid",
		"condition": "doc.incentive_paid",
		"subject": "Your Incentive Has Been Paid — {{ doc.name }}",
		"recipients": [
			_field("scouter_name"),
			_field("caller_name"),
			_field("senior_name"),
			_field("admin_name"),
			_field("additional_member_1"),
		],
	},
	# --- 6.6 Pipeline aging (weekly cadence reminders are in sales_reminders.py) --
	{
		**BASE,
		"name": "SL Pipeline Review - 30 Days Open",
		"document_type": "Opportunity",
		"event": "Days After",
		"date_changed": "creation",
		"days_in_advance": 30,
		"condition": "doc.status == 'Open'",
		"subject": "Opportunity Open 30 Days — Review Status — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin"), _role("SL Sales Supervisor")],
	},
	{
		**BASE,
		"name": "SL Pipeline Review - 60 Days Open",
		"document_type": "Opportunity",
		"event": "Days After",
		"date_changed": "creation",
		"days_in_advance": 60,
		"condition": "doc.status == 'Open'",
		"subject": "Opportunity Open 60 Days — Escalation Review — {{ doc.name }}",
		"recipients": [_role("SL Sales Admin"), _role("SL Admin"), _role("SL Management")],
	},
]


def setup_sales_module_notifications():
	create_notifications(NOTIFICATIONS, update=True)
