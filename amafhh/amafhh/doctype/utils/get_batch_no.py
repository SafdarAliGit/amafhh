import frappe


@frappe.whitelist()
def get_batch_no(batch_no):
    data = {}
    # balance = 0
    # stock = frappe.db.sql(
    #     """
    #     select
    #        SUM(CASE WHEN `tabStock Ledger Entry`.actual_qty < 0 THEN `tabStock Ledger Entry`.actual_qty ELSE 0 END) as balance_qty
    #     from `tabStock Entry`, `tabStock Ledger Entry`
    #     where `tabStock Entry`.name = `tabStock Ledger Entry`.voucher_no AND `tabStock Entry`.docstatus = 1 AND `tabStock Ledger Entry`.is_cancelled = 0
    #         AND `tabStock Entry`.batch_no =  %s
    #     """, (batch_no),
    #     as_dict=1
    # )
    # if stock[0].balance_qty and stock[0].balance_qty < 0:
    #     balance = stock[0].balance_qty
    batch_doc = frappe.get_doc("Batch", batch_no)
    if batch_doc:
        data.update(
            {
                "item_code": batch_doc.item,
                "rate": batch_doc.rate,
                "amount": batch_doc.amount,
                # "weight_balance": float(batch_doc.batch_qty) + balance,
                "weight_balance": float(batch_doc.batch_qty),
                "batch_id": batch_doc.batch_id,
                "import_file": batch_doc.import_file
            }
        )
        item = frappe.get_doc("Item", batch_doc.item)
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
