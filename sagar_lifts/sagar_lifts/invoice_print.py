"""Numbers for the Tax Invoice print format's milestone table (paper SL/238/26-27).

Per Sales Order milestone: % of contract, Pre (billed on earlier submitted
invoices of the same job and type — Tax Invoices for a TI, Proformas for a PI), Curr (this invoice), Total = Pre + Curr, Amt = Total
% of the contract. A = cumulative billed, B = previous bills (Pre % of the
contract), C = this invoice's net total — equals A - B when the invoice amount
matches its milestone %."""

import frappe
from frappe.utils import cint, flt

from sagar_lifts.sagar_lifts.setup.sales_order import MILESTONE_COUNT


def milestone_bill(doc):
	so = frappe.get_doc("Sales Order", doc.job_id)
	contract = flt(so.net_total)
	previous = frappe.get_all(
		"Sales Invoice",
		filters={
			"job_id": doc.job_id,
			"pi_type": doc.pi_type,
			"billing_trigger_type": "Milestone",
			"docstatus": 1,
			"name": ("!=", doc.name),
			"posting_date": ("<=", doc.posting_date),
		},
		fields=["milestone_number", "milestone_percent"],
	)
	rows = []
	for n in range(1, MILESTONE_COUNT + 1):
		percent = flt(so.get(f"milestone_{n}_percent"))
		if not percent:
			continue
		pre = min(sum(flt(p.milestone_percent) for p in previous if cint(p.milestone_number) == n), percent)
		curr = flt(doc.milestone_percent) if cint(doc.milestone_number) == n else 0
		rows.append({
			"label": so.get(f"milestone_{n}_name"),
			"percent": percent,
			"pre": pre,
			"curr": curr,
			"total": pre + curr,
			"amount": contract * (pre + curr) / 100,
		})
	a = sum(r["amount"] for r in rows)
	b = contract * sum(r["pre"] for r in rows) / 100
	return {"so": so, "contract": contract, "rows": rows, "a": a, "b": b, "c": flt(doc.net_total)}


def demo():
	"""bench --site sagar.lifts execute sagar_lifts.sagar_lifts.invoice_print.demo — paper SL/238 numbers."""
	so = frappe._dict(net_total=1450000)
	for n, (name, pct) in enumerate([("Advance", 10), ("Material Delivery", 50), ("Erection", 30), ("Completion", 10)], 1):
		so[f"milestone_{n}_name"], so[f"milestone_{n}_percent"] = name, pct
	doc = frappe._dict(name="X", job_id="J", posting_date="2026-05-13", milestone_number=4, milestone_percent=10, net_total=145000)
	prev = [frappe._dict(milestone_number=n, milestone_percent=p) for n, p in [(1, 10), (2, 50), (3, 30)]]
	orig_doc, orig_all = frappe.get_doc, frappe.get_all
	frappe.get_doc, frappe.get_all = (lambda *a, **k: so), (lambda *a, **k: prev)
	try:
		out = milestone_bill(doc)
	finally:
		frappe.get_doc, frappe.get_all = orig_doc, orig_all
	assert [(r["pre"], r["curr"], r["amount"]) for r in out["rows"]] == [
		(10, 0, 145000), (50, 0, 725000), (30, 0, 435000), (0, 10, 145000)
	], out["rows"]
	assert (out["a"], out["b"], out["c"]) == (1450000, 1305000, 145000)
	print("ok")
