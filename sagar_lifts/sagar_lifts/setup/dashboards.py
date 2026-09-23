"""Dashboards — No-Code Guide Section 14, extended to one per SL role.

SL Admin and SL Management share "Sagar Lifts Management" — they need the
same full view, so no separate copy. SL Technician gets none: the guide is
explicit that role is "Mobile view only — no desktop workspace," so a
Desk dashboard would contradict the role's own definition.
"""

import frappe

NUMBER_CARDS = [
	{
		"name": "Total Outstanding",
		"document_type": "Sales Invoice",
		"function": "Sum",
		"aggregate_function_based_on": "outstanding_amount",
		"filters_json": '[["Sales Invoice","status","in",["Unpaid","Overdue"]]]',
	},
	{
		"name": "Active Orders",
		"document_type": "Sales Order",
		"function": "Count",
		"filters_json": '[["Sales Order","deployment_status","!=","Dismantled"]]',
	},
	{
		"name": "Bad Debt Risk",
		"document_type": "Sales Invoice",
		"function": "Count",
		# ERPNext has no stored "days overdue" field — "Overdue" status is the
		# closest native proxy. The guide's 90-day threshold needs a saved
		# Report (date math) to enforce exactly; this card is a headline count.
		"filters_json": '[["Sales Invoice","status","=","Overdue"]]',
	},
	{
		"name": "PM Overdue This Month",
		"document_type": "Sales Order",
		"function": "Count",
		# Uses the pm_visit_overdue flag (setup/sales_order.py + tasks.py)
		# rather than reconstructing "no visit logged this month" here.
		"filters_json": '[["Sales Order","pm_visit_overdue","=",1]]',
	},
	{
		"name": "Purchase Orders Pending Approval",
		"document_type": "Purchase Order",
		"function": "Count",
		"filters_json": '[["Purchase Order","po_approval_status","=","Pending Approval"]]',
	},
	{
		"name": "Orders Ready to Dispatch",
		"document_type": "Sales Order",
		"function": "Count",
		"filters_json": '[["Sales Order","deployment_status","=","Active"],'
		'["Sales Order","advance_received","=",1]]',
	},
	{
		"name": "Dispatched Awaiting Installation",
		"document_type": "Sales Order",
		"function": "Count",
		"filters_json": '[["Sales Order","deployment_status","=","Dispatched"]]',
	},
	{
		"name": "Active AMC Orders",
		"document_type": "Sales Order",
		"function": "Count",
		"filters_json": '[["Sales Order","deployment_status","=","AMC"]]',
	},
	{
		"name": "BOMs Pending Components",
		"document_type": "BOM",
		"function": "Count",
		# Draft BOM shells auto-created by sales_order_create_bom_skeleton —
		# still need someone to add the actual components and submit.
		"filters_json": '[["BOM","docstatus","=",0]]',
	},
]

DASHBOARD_CHARTS = [
	{
		"name": "Outstanding by Developer",
		"chart_type": "Group By",
		"document_type": "Sales Invoice",
		"group_by_type": "Sum",
		"group_by_based_on": "customer",
		"aggregate_function_based_on": "outstanding_amount",
		"type": "Bar",
		"timespan": "Last Year",
		"filters_json": '[["Sales Invoice","status","in",["Unpaid","Overdue"]]]',
	},
	{
		"name": "Collections by Month",
		"chart_type": "Sum",
		"document_type": "Payment Entry",
		"based_on": "posting_date",
		"value_based_on": "paid_amount",
		"time_interval": "Monthly",
		"timeseries": 1,
		"type": "Line",
		"timespan": "Last Year",
		"filters_json": '[["Payment Entry","payment_type","=","Receive"],["Payment Entry","docstatus","=",1]]',
	},
	{
		"name": "Orders by Status",
		"chart_type": "Group By",
		"document_type": "Sales Order",
		"group_by_type": "Count",
		"group_by_based_on": "deployment_status",
		"type": "Pie",
		"timespan": "Last Year",
		"filters_json": "[]",
	},
]

# dashboard_name -> (card names, chart names)
DASHBOARDS = {
	"Sagar Lifts Management": (
		["Total Outstanding", "Active Orders", "Bad Debt Risk", "PM Overdue This Month"],
		["Outstanding by Developer", "Collections by Month", "Orders by Status"],
	),
	"Sagar Lifts - Collection Lead": (
		["Total Outstanding", "Active Orders"],
		["Outstanding by Developer"],
	),
	"Sagar Lifts - Billing": (
		["Total Outstanding", "Bad Debt Risk"],
		["Outstanding by Developer", "Collections by Month"],
	),
	"Sagar Lifts - Manufacturing": (
		["Active Orders", "BOMs Pending Components"],
		["Orders by Status"],
	),
	"Sagar Lifts - Stores": (
		["Purchase Orders Pending Approval"],
		# Dashboard.charts is a mandatory table — every dashboard needs at
		# least one, even a role with no chart of its own design.
		["Orders by Status"],
	),
	"Sagar Lifts - Dispatch": (
		["Orders Ready to Dispatch", "Dispatched Awaiting Installation"],
		["Orders by Status"],
	),
	"Sagar Lifts - Service Manager": (
		["PM Overdue This Month", "Active AMC Orders"],
		["Orders by Status"],
	),
}


def _upsert(doctype, name, values, key_field):
	if frappe.db.exists(doctype, name):
		doc = frappe.get_doc(doctype, name)
	else:
		doc = frappe.new_doc(doctype)
		doc.set(key_field, name)
	for field, value in values.items():
		doc.set(field, value)
	doc.is_public = 1
	doc.save(ignore_permissions=True)
	return doc


def setup_dashboards():
	for card in NUMBER_CARDS:
		values = {k: v for k, v in card.items() if k != "name"}
		values["label"] = card["name"]
		_upsert("Number Card", card["name"], values, "label")

	for chart in DASHBOARD_CHARTS:
		values = {k: v for k, v in chart.items() if k != "name"}
		values["chart_name"] = chart["name"]
		_upsert("Dashboard Chart", chart["name"], values, "chart_name")

	for dashboard_name, (card_names, chart_names) in DASHBOARDS.items():
		if frappe.db.exists("Dashboard", dashboard_name):
			dash = frappe.get_doc("Dashboard", dashboard_name)
		else:
			dash = frappe.new_doc("Dashboard")
			dash.dashboard_name = dashboard_name

		dash.set("cards", [])
		for card_name in card_names:
			dash.append("cards", {"card": card_name})

		dash.set("charts", [])
		for chart_name in chart_names:
			dash.append("charts", {"chart": chart_name})

		dash.is_default = 0
		dash.save(ignore_permissions=True)
