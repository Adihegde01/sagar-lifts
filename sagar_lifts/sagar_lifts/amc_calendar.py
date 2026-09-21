"""AMC Billing Calendar (Indian Financial Year: April - March).

Quarter | Months            | Last Day  | PM PI Deadline
Q1      | Apr, May, Jun     | 30 Jun    | 5 Jul
Q2      | Jul, Aug, Sep     | 30 Sep    | 5 Oct
Q3      | Oct, Nov, Dec     | 31 Dec    | 5 Jan
Q4      | Jan, Feb, Mar     | 31 Mar    | 5 Apr
"""

from frappe.utils import add_days, get_last_day, getdate

# month -> (quarter, 1-indexed position of that month within the quarter)
_MONTH_INFO = {
	4: ("Q1", 1),
	5: ("Q1", 2),
	6: ("Q1", 3),
	7: ("Q2", 1),
	8: ("Q2", 2),
	9: ("Q2", 3),
	10: ("Q3", 1),
	11: ("Q3", 2),
	12: ("Q3", 3),
	1: ("Q4", 1),
	2: ("Q4", 2),
	3: ("Q4", 3),
}


def get_quarter(date):
	"""'Q1'-'Q4' for the Indian FY quarter containing `date`."""
	return _MONTH_INFO[getdate(date).month][0]


def get_pm_month(date):
	"""'Month 1'/'Month 2'/'Month 3' — this date's position within its quarter."""
	return f"Month {_MONTH_INFO[getdate(date).month][1]}"


def get_quarter_end(date):
	"""Last day of the quarter containing `date` (30 Jun / 30 Sep / 31 Dec / 31 Mar)."""
	date = getdate(date)
	_, position = _MONTH_INFO[date.month]
	# the quarter's last month is (3 - position) months after this date's month
	year, month = date.year, date.month + (3 - position)
	if month > 12:
		year, month = year + 1, month - 12
	return get_last_day(getdate(f"{year}-{month:02d}-01"))


def get_quarter_start(date):
	"""First day of the quarter containing `date` (1 Apr / 1 Jul / 1 Oct / 1 Jan)."""
	date = getdate(date)
	_, position = _MONTH_INFO[date.month]
	# the quarter's first month is (position - 1) months before this date's month
	year, month = date.year, date.month - (position - 1)
	if month < 1:
		year, month = year - 1, month + 12
	return getdate(f"{year}-{month:02d}-01")


def get_pi_deadline(date):
	"""Last day for the PM PI covering `date`'s quarter to be raised by (quarter end + 5 days)."""
	return add_days(get_quarter_end(date), 5)


def get_last_completed_quarter(today):
	"""(quarter_label, quarter_end, deadline) for the FY quarter just before `today`'s quarter."""
	prev_quarter_end = add_days(get_quarter_start(today), -1)
	return get_quarter(prev_quarter_end), prev_quarter_end, get_pi_deadline(prev_quarter_end)
