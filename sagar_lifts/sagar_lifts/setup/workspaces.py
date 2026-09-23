"""Workspaces — one per SL role, restricted via the native `roles` table so
each role only sees their own in the sidebar. A Dashboard (setup/dashboards.py)
only holds cards/charts — no navigation. Workspace is Frappe's actual answer
for "details + navigation" together: shortcuts to the doctypes that role
works in, plus the same cards/charts, all on one page.

SL Admin/SL Management share one (same full oversight view, matching the
Dashboard split). SL Technician gets none — mobile-only, no desktop
workspace, per the guide's own definition of that role.
"""

import json

import frappe

# role -> (workspace title, [(doctype, label), ...] shortcuts, [card names], [chart names])
WORKSPACES = {
	"SL Admin": (
		"Sagar Lifts Management",
		[
			("Sales Order", "Sales Orders"),
			("Delivery Note", "Delivery Notes"),
			("Sales Invoice", "Sales Invoices"),
			("Purchase Order", "Purchase Orders"),
			("Maintenance Visit", "Maintenance Visits"),
		],
		["Total Outstanding", "Active Orders", "Bad Debt Risk", "PM Overdue This Month"],
		["Outstanding by Developer", "Collections by Month", "Orders by Status"],
	),
	"SL Management": (
		"Sagar Lifts Management",
		[
			("Sales Order", "Sales Orders"),
			("Delivery Note", "Delivery Notes"),
			("Sales Invoice", "Sales Invoices"),
			("Purchase Order", "Purchase Orders"),
			("Maintenance Visit", "Maintenance Visits"),
		],
		["Total Outstanding", "Active Orders", "Bad Debt Risk", "PM Overdue This Month"],
		["Outstanding by Developer", "Collections by Month", "Orders by Status"],
	),
	"SL Collection Lead": (
		"Sagar Lifts - Collection Lead",
		[
			("Sales Order", "Sales Orders"),
			("Sales Invoice", "Sales Invoices"),
			("Customer", "Developers"),
		],
		["Total Outstanding", "Active Orders"],
		["Outstanding by Developer"],
	),
	"SL Billing": (
		"Sagar Lifts - Billing",
		[
			("Sales Invoice", "Sales Invoices"),
			("Purchase Invoice", "Purchase Invoices"),
			("Payment Entry", "Payment Entries"),
			("Sales Order", "Sales Orders"),
		],
		["Total Outstanding", "Bad Debt Risk"],
		["Outstanding by Developer", "Collections by Month"],
	),
	"SL Manufacturing": (
		"Sagar Lifts - Manufacturing",
		[
			("Sales Order", "Sales Orders"),
			("BOM", "Bills of Material"),
			("Purchase Order", "Purchase Orders"),
			("Project", "Projects"),
		],
		["Active Orders", "BOMs Pending Components"],
		["Orders by Status"],
	),
	"SL Stores": (
		"Sagar Lifts - Stores",
		[
			("Purchase Order", "Purchase Orders"),
			("Material Request", "Material Requests"),
			("Delivery Note", "Delivery Notes"),
			("Item", "Items"),
		],
		["Purchase Orders Pending Approval"],
		["Orders by Status"],
	),
	"SL Dispatch": (
		"Sagar Lifts - Dispatch",
		[
			("Delivery Note", "Delivery Notes"),
			("Sales Order", "Sales Orders"),
		],
		["Orders Ready to Dispatch", "Dispatched Awaiting Installation"],
		["Orders by Status"],
	),
	"SL Service Manager": (
		"Sagar Lifts - Service Manager",
		[
			("Maintenance Visit", "Maintenance Visits"),
			("Maintenance Schedule", "Maintenance Schedules"),
			("Sales Order", "Sales Orders"),
		],
		["PM Overdue This Month", "Active AMC Orders"],
		["Orders by Status"],
	),
}


def _build_content(shortcuts, cards, charts):
	blocks = []
	if shortcuts:
		blocks.append({"type": "header", "data": {"text": '<span class="h4"><b>Shortcuts</b></span>', "col": 12}})
		for _doctype, label in shortcuts:
			blocks.append({"type": "shortcut", "data": {"shortcut_name": label, "col": 3}})
		blocks.append({"type": "spacer", "data": {"col": 12}})
	if cards or charts:
		blocks.append({"type": "header", "data": {"text": '<span class="h4"><b>Overview</b></span>', "col": 12}})
		for card in cards:
			blocks.append({"type": "number_card", "data": {"number_card_name": card, "col": 4}})
		for chart in charts:
			blocks.append({"type": "chart", "data": {"chart_name": chart, "col": 12}})
	for i, block in enumerate(blocks):
		block["id"] = f"block-{i}"
	return json.dumps(blocks)


def setup_workspaces():
	# Two roles (Admin, Management) share one workspace — build it once,
	# then attach both roles to the same document.
	by_title = {}
	for role, (title, shortcuts, cards, charts) in WORKSPACES.items():
		by_title.setdefault(title, {"roles": [], "shortcuts": shortcuts, "cards": cards, "charts": charts})
		by_title[title]["roles"].append(role)

	for idx, (title, spec) in enumerate(by_title.items()):
		if frappe.db.exists("Workspace", title):
			ws = frappe.get_doc("Workspace", title)
		else:
			ws = frappe.new_doc("Workspace")
			ws.label = title

		ws.title = title
		ws.public = 1
		ws.is_hidden = 0
		# Without `app`, the workspace has no app-switcher group to slot into
		# and never appears in the sidebar at all — confirmed live, this was
		# the actual bug behind "must contain shortcuts": the shortcuts were
		# always there, the workspace itself just wasn't showing up.
		ws.app = "sagar_lifts"
		if not ws.sequence_id:
			ws.sequence_id = idx + 1

		ws.set("shortcuts", [])
		for doctype, label in spec["shortcuts"]:
			ws.append(
				"shortcuts",
				{"type": "DocType", "link_to": doctype, "label": label, "doc_view": "List"},
			)

		ws.set("number_cards", [])
		for card in spec["cards"]:
			ws.append("number_cards", {"number_card_name": card, "label": card})

		ws.set("charts", [])
		for chart in spec["charts"]:
			ws.append("charts", {"chart_name": chart, "label": chart})

		ws.set("roles", [])
		for role in spec["roles"]:
			ws.append("roles", {"role": role})

		ws.content = _build_content(spec["shortcuts"], spec["cards"], spec["charts"])
		ws.save(ignore_permissions=True)
