from sagar_lifts.sagar_lifts.setup.roles import create_sl_roles


def execute():
	# create_sl_roles() also (re)points SL Technician's home_page at the new
	# chrome-free portal page — the original create_sl_roles patch already
	# ran on existing sites before that page existed, so re-run it here.
	create_sl_roles()
