"""Notification & Alert Specification (implementation plan, Section 8).

Every automation trigger delivered as a Frappe Notification — Email plus a
System Notification (bell icon) — rather than as custom code. Recipients are
either a Role (everyone holding it gets notified) or a document field holding
a User (e.g. the Collection Lead resolved for that invoice's job).

Two adaptations from the plan's literal wording, called out inline below:
  - PM Overdue targets Maintenance Schedule Detail, which has no sales_order
    field of its own; the subject uses the item/parent schedule instead.
  - The escalation ladder adds `outstanding_amount > 0` to every rung so a
    settled invoice doesn't keep re-alerting — implicit in "escalation",
    not spelled out in the plan's trigger table.
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
	# --- Event-based notifications ---------------------------------------
	{
		**BASE,
		"name": "SL New Order - Billing",
		"document_type": "Sales Order",
		"event": "Submit",
		"subject": "New Order Confirmed — Raise Advance PI",
		"recipients": [_role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL New Order - Manufacturing",
		"document_type": "Sales Order",
		"event": "Submit",
		"condition": "doc.lift_type == 'Construction'",
		"subject": "New Production Order — {{ doc.name }}",
		"recipients": [_role("SL Manufacturing")],
	},
	{
		**BASE,
		"name": "SL Advance Received - Dispatch",
		"document_type": "Sales Order",
		"event": "Value Change",
		"value_changed": "advance_received",
		"condition": "doc.advance_received == 1",
		"subject": "Dispatch Cleared — Advance Received — {{ doc.name }}",
		"recipients": [_role("SL Dispatch")],
	},
	{
		**BASE,
		"name": "SL Dispatch Done - Billing",
		"document_type": "Delivery Note",
		"event": "Submit",
		"subject": "Material Dispatched — Raise On Delivery PI",
		"recipients": [_role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL Dispatch Done - Dispatch Reminder",
		"document_type": "Delivery Note",
		"event": "Submit",
		"subject": "Action Required — Collect Signed Challan",
		"recipients": [_role("SL Dispatch")],
	},
	{
		**BASE,
		"name": "SL Handover - Service Manager",
		"document_type": "Sales Order",
		"event": "Value Change",
		"value_changed": "deployment_status",
		"condition": "doc.deployment_status == 'Handed Over'",
		"subject": "New Lift Handed Over — Add to Maintenance Route",
		"recipients": [_role("SL Service Manager")],
	},
	{
		**BASE,
		"name": "SL Handover - Billing",
		"document_type": "Sales Order",
		"event": "Value Change",
		"value_changed": "deployment_status",
		"condition": "doc.deployment_status == 'Handed Over'",
		"subject": "Handover Confirmed — Raise Handover PI",
		"recipients": [_role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL AMC Period Starts",
		"document_type": "Sales Order",
		"event": "Days After",
		"date_changed": "amc_start_date",
		"days_in_advance": 0,
		"subject": "AMC Now Active — {{ doc.name }}",
		"recipients": [_role("SL Billing"), _role("SL Service Manager")],
	},
	{
		**BASE,
		"name": "SL PM Overdue",
		"document_type": "Maintenance Schedule Detail",
		"event": "Days After",
		"date_changed": "scheduled_date",
		"days_in_advance": 25,
		"condition": "doc.completion_status != 'Fully Completed'",
		"subject": "PM OVERDUE — {{ doc.item_name }} ({{ doc.parent }})",
		"recipients": [_role("SL Service Manager"), _role("SL Admin"), _role("SL Management")],
	},
	{
		**BASE,
		"name": "SL Previous PI Unpaid Warning",
		"document_type": "Sales Invoice",
		"event": "Save",
		"condition": (
			"doc.job_id and frappe.db.exists('Sales Invoice', "
			"{'job_id': doc.job_id, 'status': 'Unpaid', 'docstatus': 1, 'name': ['!=', doc.name]})"
		),
		"subject": "Warning — Previous PI Unpaid for This Order",
		"recipients": [_role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL Dismantling Confirmed",
		"document_type": "Sales Order",
		"event": "Value Change",
		"value_changed": "deployment_status",
		"condition": "doc.deployment_status == 'Dismantled'",
		"subject": "Lift Dismantled — Action Required",
		"recipients": [_role("SL Billing"), _role("SL Service Manager")],
	},
	{
		**BASE,
		"name": "SL Contractor Bill Approved",
		"document_type": "Purchase Invoice",
		"event": "Value Change",
		"value_changed": "approved_by_manufacturing",
		"condition": "doc.bill_type == 'Contractor' and doc.approved_by_manufacturing == 1",
		"subject": "Contractor Bill Approved — Process Payment",
		"recipients": [_role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL Outstanding Flag - All Sites",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 1,
		"condition": "doc.status == 'Overdue'",
		"subject": "Outstanding Flag — All Sites of {{ doc.customer_name }} Flagged",
		"recipients": [_role("SL Service Manager"), _role("SL Billing")],
	},
	# --- Outstanding-escalation ladder (Sales Invoice, Days Before/After Due) --
	{
		**BASE,
		"name": "SL Payment Due 7 Days Before",
		"document_type": "Sales Invoice",
		"event": "Days Before",
		"date_changed": "due_date",
		"days_in_advance": 7,
		"condition": "doc.outstanding_amount > 0",
		"subject": "Payment Due in 7 Days — {{ doc.name }} — {{ doc.customer_name }}",
		"recipients": [_field("collection_lead")],
	},
	{
		**BASE,
		"name": "SL Payment Due Today",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 0,
		"condition": "doc.outstanding_amount > 0",
		"subject": "PAYMENT DUE TODAY — {{ doc.name }} — ₹{{ doc.outstanding_amount }}",
		"recipients": [_field("collection_lead"), _role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL Overdue 7 Days",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 7,
		"condition": "doc.outstanding_amount > 0",
		"subject": "OVERDUE 7 Days — {{ doc.name }} — ₹{{ doc.outstanding_amount }}",
		"recipients": [_field("collection_lead"), _role("SL Billing")],
	},
	{
		**BASE,
		"name": "SL Overdue 15 Days",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 15,
		"condition": "doc.outstanding_amount > 0",
		"subject": "OVERDUE 15 Days — Management Alerted — {{ doc.name }}",
		"recipients": [_field("collection_lead"), _role("SL Billing"), _role("SL Management")],
	},
	{
		**BASE,
		"name": "SL Overdue 30 Days",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 30,
		"condition": "doc.outstanding_amount > 0",
		"subject": "OVERDUE 30 Days — Developer Account Flagged — {{ doc.name }}",
		"recipients": [_field("collection_lead"), _role("SL Billing"), _role("SL Management")],
	},
	{
		**BASE,
		"name": "SL Overdue 60 Days",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 60,
		"condition": "doc.outstanding_amount > 0",
		"subject": "URGENT — 60 Days Overdue — Personal Review Required",
		"recipients": [_role("SL Management")],
	},
	{
		**BASE,
		"name": "SL Overdue 90 Plus Days",
		"document_type": "Sales Invoice",
		"event": "Days After",
		"date_changed": "due_date",
		"days_in_advance": 90,
		"condition": "doc.outstanding_amount > 0",
		"subject": "BAD DEBT RISK — 90+ Days — {{ doc.customer_name }}",
		"recipients": [_role("SL Management")],
	},
]


def setup_notifications():
	create_notifications(NOTIFICATIONS, update=True)
