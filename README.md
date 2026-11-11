# Calcrule to calculate Paymen fees for payment source


 This calculation will, for the selected level and product, calculate how much the insurance need to pay the payment platform for the fee for payment service
 
 it create bill for the payment platform based on the contribution made through that platform attached to invoice item
 
 https://openimis.atlassian.net/wiki/spaces/OP/pages/3045818376/Payment+plan+calculation+rule+fees

 Each invoice payment of the period whose invoice bills the product (a policy line, or a contract
 contribution plan detail line) is billed **once**, however many of its lines bill the product.
 The fee is `calculation_rule.fee_rate` percent of each contribution (payment plan `json_ext`);
 without that parameter the fee is 0.
