from sagar_lifts.sagar_lifts.setup.deployment_workflow import setup_deployment_workflow
from sagar_lifts.sagar_lifts.setup.sales_order import setup_sales_order_customization


def execute():
	# Draft has to be a valid Deployment Status option before the workflow
	# (and the draft orders it moves) can use it.
	setup_sales_order_customization()
	setup_deployment_workflow()
