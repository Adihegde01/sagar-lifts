# Copyright (c) 2026, Sagar Lifts and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

SHARE_AMOUNT_FIELDS = (
	"scouter_share",
	"caller_share",
	"senior_share",
	"admin_share",
	"additional_member_1_share",
)
SHARE_PERCENT_FIELDS = (
	"scouter_share_percent",
	"caller_share_percent",
	"senior_share_percent",
	"admin_share_percent",
)


class SLIncentiveRecord(Document):
	def validate(self):
		self.total_shares_allocated = sum(flt(self.get(f)) for f in SHARE_AMOUNT_FIELDS)
		self.total_percent_allocated = sum(flt(self.get(f)) for f in SHARE_PERCENT_FIELDS)
		self.balance_unallocated = flt(self.total_incentive_amount) - flt(self.total_shares_allocated)

	def before_submit(self):
		# "Total Shares Allocated must equal Total Incentive Amount before the
		# record can be submitted. Sales Admin must account for every rupee."
		# (Section 5, MUST) — only enforced at submit, so a draft can still be
		# saved while the split is being worked out.
		if abs(flt(self.balance_unallocated)) > 0.01:
			frappe.throw(
				_(
					"Total Shares Allocated (₹{0}) must equal Total Incentive Amount (₹{1}) "
					"before this record can be submitted — every rupee must be accounted for."
				).format(self.total_shares_allocated, self.total_incentive_amount)
			)
