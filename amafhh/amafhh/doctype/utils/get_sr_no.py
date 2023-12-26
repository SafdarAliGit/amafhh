import frappe


@frappe.whitelist()
def get_sr_no(sr_no):
    data = {}
    balance = 0
    stock = frappe.db.sql(
        """
        select 
           SUM(CASE WHEN `tabStock Ledger Entry`.actual_qty < 0 THEN `tabStock Ledger Entry`.actual_qty ELSE 0 END) as balance_qty
        from `tabStock Entry`, `tabStock Ledger Entry`
        where `tabStock Entry`.name = `tabStock Ledger Entry`.voucher_no AND `tabStock Entry`.docstatus = 1 AND `tabStock Ledger Entry`.is_cancelled = 0
            AND `tabStock Entry`.sr_no =  %s  
        """, (sr_no),
        as_dict=1
    )
    if stock[0].balance_qty and stock[0].balance_qty<0:
        balance = stock[0].balance_qty
    sr_no_doc = frappe.get_doc("SR NO", sr_no)
    if sr_no_doc:
        data.update(
            {
                "item_code": sr_no_doc.item_code,
                "rate": sr_no_doc.rate,
                "amount": sr_no_doc.amount,
                "weight_balance":float(sr_no_doc.weight_total) + balance,
            }
        )
        item = frappe.get_doc("Item", sr_no_doc.item_code)
        if item:
            data.update(
                {
                    "width": item.width,
                    "gsm": item.gsm,
                    "length_source": item.length,
                }
            )
        return data
    return None
