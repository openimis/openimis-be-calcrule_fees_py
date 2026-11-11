import datetime
from unittest import mock

from django.test import TestCase

from calcrule_fees.calculation_rule import FeesCalculationRule
from contribution.models import Premium
from contribution_plan.models import PaymentPlan
from core.test_helpers import create_test_interactive_user
from invoice.tests.helpers import create_test_invoice, create_test_invoice_line_item, create_test_invoice_payment
from policy.test_helpers import create_test_policy
from insuree.test_helpers import create_test_insuree
from product.test_helpers import create_test_product


class FeesCalculationRuleTest(TestCase):
    """OP-3322: each payment is billed once; missing payment plan params give no fee."""

    rule = FeesCalculationRule

    def test_fee_without_calculation_rule_params(self):
        premium = Premium(amount=200)
        for json_ext in (None, {}, {"other": 1}, '{"other": 1}'):
            with self.subTest(json_ext=json_ext):
                fee = self.rule._calculate_fee(premium, payment_plan=PaymentPlan(json_ext=json_ext))
                self.assertEqual(fee, 0)

    def test_fee_from_rate(self):
        payment_plan = PaymentPlan(json_ext='{"calculation_rule": {"fee_rate": 5}}')
        self.assertEqual(self.rule._calculate_fee(Premium(amount=200), payment_plan=payment_plan), 10)

    def test_batch_payment_bills_each_payment_once(self):
        product = create_test_product("FEES1", custom_props={"insurance_period": 12})
        invoice = create_test_invoice(code="FEES-INV-1")
        for code in ("FEES-LINE-1", "FEES-LINE-2"):
            policy = create_test_policy(product=product, insuree=create_test_insuree(with_family=True))
            create_test_invoice_line_item(invoice=invoice, line_item=policy, code=code)
        payment = create_test_invoice_payment(invoice=invoice)
        user = create_test_interactive_user(username="feesbatchuser")
        now = datetime.datetime.now()

        with mock.patch.object(FeesCalculationRule, "run_convert") as run_convert:
            self.rule._calculate_batch_payment(
                PaymentPlan(),
                context="BatchPayment",
                audit_user_id=user.i_user.id,
                start_date=now - datetime.timedelta(days=1),
                end_date=now + datetime.timedelta(days=1),
                work_data={"product": product, "created_run": None},
            )

        billed = [call.kwargs["payment"] for call in run_convert.call_args_list]
        self.assertEqual(billed, [payment])
