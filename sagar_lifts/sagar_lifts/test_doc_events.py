"""Self-check for the branching helpers in doc_events.py.

Run: bench --site <site> execute sagar_lifts.sagar_lifts.test_doc_events.demo
"""

import frappe
from frappe.utils import add_days, today

from sagar_lifts.sagar_lifts.doc_events import _depends_on_holds, get_outstanding_escalation


def demo():
	D = frappe._dict
	over_limit = 'eval:doc.bill_type=="Contractor" && !doc.labour_bill_within_limit'

	# depends-on translator: bare fieldname, ==, !=, &&, !
	assert _depends_on_holds(D(shortage_noted=1), "shortage_noted")
	assert not _depends_on_holds(D(shortage_noted=0), "shortage_noted")
	assert _depends_on_holds(D(docstatus=0), "eval:doc.docstatus==0")
	assert not _depends_on_holds(D(docstatus=1), "eval:doc.docstatus==0")
	assert _depends_on_holds(D(bill_type="Contractor", labour_bill_within_limit=0), over_limit)
	assert not _depends_on_holds(D(bill_type="Contractor", labour_bill_within_limit=1), over_limit)
	assert not _depends_on_holds(D(bill_type="Supplier", labour_bill_within_limit=0), over_limit)
	assert _depends_on_holds(D(x="a"), 'eval:doc.x!="b"')

	# escalation ladder boundaries; paid invoices never escalate
	def level(days_past_due, outstanding=1000):
		return get_outstanding_escalation(add_days(today(), -days_past_due), outstanding)[1]

	assert level(-3) == level(0) == "None"
	assert level(1) == level(6) == "Level 1 — CL"
	assert level(7) == level(14) == "Level 2 — Billing"
	assert level(15) == level(89) == "Level 3 — Management"
	assert level(90) == "Level 4 — Bad Debt"
	assert level(200, outstanding=0) == "None"

	print("doc_events: all checks passed")
