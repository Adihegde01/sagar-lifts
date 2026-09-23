"""PO Approval Workflow — No-Code Guide Section 10.2.

Purchase Order, state field: PO Approval Status (a dedicated custom field,
not the native `status` — see setup/purchase_order.py for why).

Draft/Pending Approval/Approved all stay at docstatus 0 (pre-submission
approval stages); "Send to Supplier" is what actually submits the PO — that
matches real usage: a PO only takes effect (GRN-linkable, affects stock
projections) once submitted, and submission is the natural point an
approved order gets sent to the supplier.

Multiple "Allow Edit" roles per state use the same repeated-row pattern as
setup/deployment_workflow.py — see that file's docstring for why.
"""

import frappe

WORKFLOW_NAME = "PO Approval"

STATE_DOC_STATUS = {
	"Draft": "0",
	"Pending Approval": "0",
	"Approved": "0",
	"Ordered": "1",
}

# (state, allow_edit role)
STATE_ROLE_ROWS = [
	("Draft", "SL Stores"),
	("Pending Approval", "SL Stores"),
	("Approved", "SL Stores"),
	("Approved", "SL Admin"),
	("Ordered", "SL Stores"),
]

# (from_state, next_state, action, [roles...])
TRANSITIONS = [
	("Draft", "Pending Approval", "Submit for Approval", ["SL Stores"]),
	("Pending Approval", "Approved", "Approve PO", ["SL Stores", "SL Admin"]),
	("Approved", "Ordered", "Send to Supplier", ["SL Stores"]),
]


def _ensure_workflow_states():
	for state in STATE_DOC_STATUS:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state}).insert(
				ignore_permissions=True
			)


def _ensure_workflow_actions():
	for _from, _to, action, _roles in TRANSITIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)


def setup_po_approval_workflow():
	_ensure_workflow_states()
	_ensure_workflow_actions()

	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		wf = frappe.get_doc("Workflow", WORKFLOW_NAME)
	else:
		wf = frappe.new_doc("Workflow")
		wf.workflow_name = WORKFLOW_NAME
		wf.document_type = "Purchase Order"
		wf.workflow_state_field = "po_approval_status"

	wf.is_active = 1
	wf.set("states", [])
	for state, role in STATE_ROLE_ROWS:
		wf.append("states", {"state": state, "doc_status": STATE_DOC_STATUS[state], "allow_edit": role})

	wf.set("transitions", [])
	for from_state, next_state, action, roles in TRANSITIONS:
		for role in roles:
			wf.append(
				"transitions",
				{"state": from_state, "action": action, "next_state": next_state, "allowed": role},
			)

	wf.save(ignore_permissions=True)
