"""Sales guide Section 9: Scouters, Callers and Seniors see only their own records.

"SL Scouter and SL Caller must never see each other's leads." Done with
permission_query_conditions (list views, reports, link search) and
has_permission (opening a record) from one set of SQL clauses, instead of a
User Permission per person that someone would have to keep up to date.

A user holding any SEE_ALL role (Supervisor, Sales Admin, Admin, ...) is not
restricted. Otherwise their roles' clauses are OR-ed: a Caller who is also a
Scouter sees the leads assigned to them plus the leads from their own reports.
"""

import frappe

SEE_ALL = {
	"Administrator",
	"System Manager",
	"SL Admin",
	"SL Management",
	"SL Sales Admin",
	"SL Sales Supervisor",
	# legacy flat sales role, from before the five-role split
	"SL Sales",
}

# doctype -> role -> SQL clause; {user} is the escaped session user
OWN_RECORDS = {
	"Lead": {
		"SL Caller": "`tabLead`.assigned_caller = {user}",
		"SL Scouter": "`tabLead`.scout_report_reference in (select name from `tabSL Scout Report`"
		" where scouter_name = {user} or owner = {user})",
		"SL Sales Senior": "`tabLead`.assigned_senior = {user}",
	},
	"SL Scout Report": {
		"SL Scouter": "(`tabSL Scout Report`.scouter_name = {user} or `tabSL Scout Report`.owner = {user})",
	},
	"SL Quotation Request": {
		"SL Caller": "(`tabSL Quotation Request`.requested_by = {user} or `tabSL Quotation Request`.owner = {user}"
		" or `tabSL Quotation Request`.caller_name = {user})",
		"SL Scouter": "(`tabSL Quotation Request`.requested_by = {user} or `tabSL Quotation Request`.owner = {user}"
		" or `tabSL Quotation Request`.scouter_name = {user})",
		"SL Sales Senior": "`tabSL Quotation Request`.senior_name = {user}",
	},
	"SL Incentive Record": {
		role: "{user} in (`tabSL Incentive Record`.scouter_name, `tabSL Incentive Record`.caller_name,"
		" `tabSL Incentive Record`.senior_name, `tabSL Incentive Record`.admin_name,"
		" `tabSL Incentive Record`.additional_member_1)"
		for role in ("SL Scouter", "SL Caller", "SL Sales Senior")
	},
}


def own_records_condition(doctype, user=None):
	"""SQL condition limiting `doctype` to the user's own records, or "" for no limit."""
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if roles & SEE_ALL:
		return ""
	clauses = [sql for role, sql in OWN_RECORDS[doctype].items() if role in roles]
	if not clauses:
		return ""  # not a sales role — the permission grid alone decides
	return "(" + " or ".join(c.format(user=frappe.db.escape(user)) for c in clauses) + ")"


def has_own_record_permission(doc, ptype=None, user=None, debug=False):
	# Frappe 16 treats a None from this hook as a denial, so "no extra limit"
	# must be True; the role grid still decides whether the role may act at all.
	if ptype == "create" or doc.is_new() or not doc.get("name"):
		return True
	condition = own_records_condition(doc.doctype, user)
	if not condition:
		return True
	return bool(frappe.db.sql(f"select 1 from `tab{doc.doctype}` where name = %s and {condition}", doc.name))


def lead_query(user=None, doctype=None):
	return own_records_condition("Lead", user)


def scout_report_query(user=None, doctype=None):
	return own_records_condition("SL Scout Report", user)


def quotation_request_query(user=None, doctype=None):
	return own_records_condition("SL Quotation Request", user)


def incentive_record_query(user=None, doctype=None):
	return own_records_condition("SL Incentive Record", user)
