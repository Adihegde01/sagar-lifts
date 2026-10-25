"""Workspaces — one per SL role, restricted via the native `roles` table so
each role only sees their own in the sidebar. A Dashboard (setup/dashboards.py)
only holds cards/charts — no navigation. Workspace is Frappe's actual answer
for "details + navigation" together: shortcuts to the doctypes that role
works in, plus the same cards/charts, all on one page.

SL Admin/SL Management share one (same full oversight view, matching the
Dashboard split). SL Technician gets none — mobile-only, no desktop
workspace, per the guide's own definition of that role.

Frappe 16's desk home is a grid of Desktop Icons; a workspace shows there only
through an icon whose label names a Workspace Sidebar. Each workspace gets
both, restricted to the same roles. They are created non-standard and owned by
Administrator: migrate deletes standard icons/sidebars that no app ships as
files, and non-standard ones are only shown when Administrator owns them.
"""

import json

import frappe

SALES_CARDS = ["Total Active Leads", "Hot Leads (A Rating)", "Meetings This Week", "Quotations Pending"]

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
	"SL Accounts Caller": (
		"Sagar Lifts - Accounts Caller",
		[
			("Sales Invoice", "Sales Invoices"),
			("Customer", "Developers"),
		],
		["Total Outstanding"],
		[],
	),
	# --- Sales Module guide Section 1.1: the five sales teams ---------------
	"SL Scouter": (
		"Sagar Lifts - Scouting",
		[
			("SL Scout Report", "Scout Reports"),
			("SL Quotation Request", "Quotation Requests"),
			("Lead", "My Leads"),
		],
		[],
		[],
	),
	"SL Caller": (
		"Sagar Lifts - Calling",
		[
			("Lead", "My Leads"),
			("SL Quotation Request", "Quotation Requests"),
			("Quotation", "Quotations"),
		],
		["Total Active Leads", "Hot Leads (A Rating)"],
		[],
	),
	"SL Sales Supervisor": (
		"Sagar Lifts - Sales Supervisor",
		[
			("Lead", "Leads"),
			("SL Scout Report", "Scout Reports"),
			("SL Quotation Request", "Quotation Requests"),
			("Opportunity", "Opportunities"),
		],
		SALES_CARDS,
		["Lead Quality Distribution", "Leads by Source"],
	),
	"SL Sales Senior": (
		"Sagar Lifts - Sales Senior",
		[
			("Opportunity", "Opportunities"),
			("Lead", "My Meetings"),
			("Quotation", "Quotations"),
		],
		["Meetings This Week"],
		["Opportunities by Stage"],
	),
	"SL Sales Admin": (
		"Sagar Lifts - Sales Admin",
		[
			("SL Scout Report", "Scout Reports"),
			("Lead", "Leads"),
			("SL Quotation Request", "Quotation Requests"),
			("Quotation", "Quotations"),
			("Opportunity", "Opportunities"),
			("Sales Order", "Sales Orders"),
			("SL Incentive Record", "Incentive Records"),
			("Customer", "Developers"),
		],
		SALES_CARDS + ["Orders This Month", "Incentives Pending Payment"],
		["Monthly Orders Confirmed", "Opportunities by Stage", "Leads by Source", "Lead Quality Distribution"],
	),
	# legacy flat sales role — same view as Sales Admin until users move over
	"SL Sales": (
		"Sagar Lifts - Sales Admin",
		[],
		[],
		[],
	),
}

# workspace title -> (desk icon label, icon, [report names] for the sidebar)
DESK = {
	"Sagar Lifts Management": ("Sagar Lifts", "building", []),
	"Sagar Lifts - Collection Lead": ("SL Collections", "hand-coins", []),
	"Sagar Lifts - Billing": ("SL Billing", "receipt", []),
	"Sagar Lifts - Manufacturing": ("SL Manufacturing", "factory", []),
	"Sagar Lifts - Stores": ("SL Stores", "package", []),
	"Sagar Lifts - Dispatch": ("SL Dispatch", "truck", []),
	"Sagar Lifts - Service Manager": ("SL Service", "wrench", []),
	"Sagar Lifts - Accounts Caller": ("SL Accounts Calling", "phone-call", []),
	"Sagar Lifts - Scouting": ("SL Scouting", "map-pin", []),
	"Sagar Lifts - Calling": ("SL Calling", "phone", ["SL Quotations Expiring This Week"]),
	"Sagar Lifts - Sales Supervisor": (
		"SL Sales Supervisor",
		"clipboard-check",
		["SL All Active Leads by Caller", "SL Leads with No Activity 7+ Days", "SL Caller Performance - Conversions"],
	),
	"Sagar Lifts - Sales Senior": ("SL Sales Senior", "handshake", []),
	"Sagar Lifts - Sales Admin": (
		"SL Sales",
		"briefcase",
		[
			"SL All Active Leads by Caller",
			"SL Leads with No Activity 7+ Days",
			"SL Quotations Expiring This Week",
			"SL Opportunity Conversion Rate",
			"SL Scouter Performance - Leads Generated",
			"SL Caller Performance - Conversions",
			"SL Monthly Incentives Paid",
			"SL Pipeline Value - Open Opportunities",
		],
	),
}

# can open every Sagar Lifts workspace and icon. SL Admin is not here: admins
# see only their own "Sagar Lifts" tile (plus any other role they hold).
SEE_ALL_WORKSPACES = ["System Manager"]


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
		spec = by_title.setdefault(title, {"roles": [], "shortcuts": shortcuts, "cards": cards, "charts": charts})
		spec["roles"].append(role)
	for spec in by_title.values():
		spec["roles"] += [r for r in SEE_ALL_WORKSPACES if r not in spec["roles"]]

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

		label, icon, reports = DESK[title]
		_desk_sidebar(label, title, icon, spec["shortcuts"], reports)
		_desk_icon(label, icon, spec["roles"], idx)

	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")


def _owned_by_admin(doctype, name):
	doc = frappe.get_doc(doctype, name) if frappe.db.exists(doctype, name) else frappe.new_doc(doctype)
	doc.flags.ignore_permissions = True
	return doc


def _desk_sidebar(label, workspace, icon, shortcuts, reports):
	sb = _owned_by_admin("Workspace Sidebar", label)
	sb.update({"title": label, "header_icon": icon, "app": "sagar_lifts", "standard": 0})
	items = [
		{"type": "Link", "label": "Home", "link_type": "Workspace", "link_to": workspace, "icon": "home"},
		# tasks assigned when a Sales Order's project is created (doc_events.PROJECT_TASKS)
		{"type": "Link", "label": "My Tasks", "link_type": "DocType", "link_to": "ToDo", "icon": "list-todo"},
	]
	items += [
		{"type": "Link", "label": lbl, "link_type": "DocType", "link_to": doctype}
		for doctype, lbl in shortcuts
	]
	if reports:
		items.append({"type": "Section Break", "label": "Reports", "icon": "sheet", "indent": 1, "collapsible": 1})
		items += [{"type": "Link", "label": r, "link_type": "Report", "link_to": r, "child": 1} for r in reports]
	sb.set("items", items)
	if sb.is_new():
		sb.name = label
		sb.insert(set_name=label)
	else:
		sb.save()
	_set_owner("Workspace Sidebar", label)


def _desk_icon(label, icon, roles, idx):
	di = _owned_by_admin("Desktop Icon", label)
	di.update({
		"label": label,
		"icon": icon,
		"icon_type": "Link",
		"link_type": "Workspace Sidebar",
		"link_to": label,
		"app": "sagar_lifts",
		"standard": 0,
		"hidden": 0,
		"bg_color": "blue",
		"idx": 100 + idx,
	})
	di.set("roles", [{"role": r} for r in roles])
	if di.is_new():
		di.insert(set_name=label)
	else:
		di.save()
	_set_owner("Desktop Icon", label)


def _set_owner(doctype, name):
	# get_desktop_icons only loads non-standard icons Administrator owns
	frappe.db.set_value(doctype, name, "owner", "Administrator", update_modified=False)
