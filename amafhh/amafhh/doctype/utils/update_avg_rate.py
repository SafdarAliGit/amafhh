import frappe


@frappe.whitelist()
def update_avg_rate(**args):
    # -----------START-------
    import_file = args.get('import_file')
    pi = frappe.qb.DocType("Purchase Invoice")
    pii = frappe.qb.DocType("Purchase Invoice Item")
    pi_parent_query = (
        frappe.qb.from_(pi)
        .select(
            pi.posting_date,
            pi.supplier,
            pi.name.as_("voucher_no"),
            frappe.qb.functions("SUM", pii.qty).as_("qty"),
            frappe.qb.functions("AVG", pii.rate).as_("rate"),
            pi.grand_total.as_("amount")
        )
        .left_join(pii).on(pi.name == pii.parent)
        .where((pi.docstatus == 1) & (pi.import_file == import_file))
        .groupby(pi.name)
        .orderby(pi.posting_date)
    )
    pi_parent_query_result = pi_parent_query.run(as_dict=True)

    si = frappe.qb.DocType("Sales Invoice")
    sii = frappe.qb.DocType("Sales Invoice Item")

    si_parent_query = (
        frappe.qb.from_(si)
        .select(
            frappe.qb.functions("SUM", sii.qty).as_("qty"),
            frappe.qb.functions("SUM", sii.amount).as_("amount")
        )
        .left_join(sii).on(si.name == sii.parent)
        .where(
            (si.docstatus == 1) &
            (sii.import_file == import_file)
        )
    )
    si_parent_query_result = si_parent_query.run(as_dict=True)

    lcv = frappe.qb.DocType("Landed Cost Voucher")
    lctc = frappe.qb.DocType("Landed Cost Taxes and Charges")
    lcv_parent_query = (
        frappe.qb.from_(lcv)
        .select(
            lcv.posting_date,
            lctc.description.as_("qty"),
            lcv.name.as_("voucher_no"),
            lctc.expense_account.as_("supplier"),
            lctc.amount
        )
        .left_join(lctc).on(lcv.name == lctc.parent)
        .where((lcv.docstatus == 1) & (lcv.import_file == import_file))
    )

    lcv_parent_query_result = lcv_parent_query.run(as_dict=True)

    # -------------Purchase Invoice----------------
    total_purchase_qty = 0
    total_rate = 0
    total_purchase_amount = 0
    for purchase in pi_parent_query_result:
        total_purchase_qty += purchase.qty if purchase.qty else 0
        total_rate += purchase.rate if purchase.rate else 0
        total_purchase_amount += purchase.amount if purchase.amount else 0

    avg_purchase_rate = total_rate / len(pi_parent_query_result) if pi_parent_query_result else 0
    # -------------Sales Invoice----------------
    total_sales_qty = 0
    total_sale_amount = 0
    total_sales_qty = si_parent_query_result[0].qty if si_parent_query_result else 0
    total_sale_amount = si_parent_query_result[0].amount if si_parent_query_result else 0
    # Check if either of the values is None
    if total_sale_amount is None or total_sales_qty is None:
        avg_sale_rate = 0
    else:
        avg_sale_rate = total_sale_amount / total_sales_qty

    # -------------Stock Balances----------------
    # item_codes = frappe.get_all("Item", filters={"import_file": import_file}, pluck="name")
    # item_codes_str = ", ".join(["%s"] * len(item_codes))
    # balance_stock = frappe.db.sql("""
    #     SELECT SUM(qty_after_transaction) AS qty_after_transaction
    #     FROM `tabStock Ledger Entry`
    #     WHERE item_code IN ({0}) AND is_cancelled = 0
    # """.format(item_codes_str), tuple(item_codes), as_dict=True)
    # total_balance_qty = balance_stock[0].qty_after_transaction if balance_stock else 0
    total_balance_qty = (total_purchase_qty if total_purchase_qty else 0) - (total_sales_qty if total_sales_qty else 0)

    # -------------Landed Cost Voucher----------------
    total_lc_amount = sum(lcr.amount for lcr in lcv_parent_query_result)

    total_cost = total_purchase_amount + total_lc_amount
    avg_rate_with_lc = total_cost / total_purchase_qty if total_purchase_qty != 0 else 0

    balance_stock_value = total_balance_qty * avg_rate_with_lc
    cogs = total_cost - balance_stock_value
    profit_and_loss = (total_sale_amount if total_sale_amount else 0) - (cogs if cogs else 0)
    # DAMAGED , NON PHYSICAL, UNDELIVERED STOCK
    stock_damage_query = f"""
                SELECT 
                    COALESCE(SUM(CASE WHEN sle.warehouse = 'Damaged - A' THEN sle.actual_qty ELSE 0 END), 0) AS damaged,
                    COALESCE(SUM(CASE WHEN sle.warehouse = 'Non Fisical Damage - A' THEN sle.actual_qty ELSE 0 END), 0) AS non_physical,
                    COALESCE(SUM(CASE WHEN sle.warehouse = 'Un delivered. Warehouse - A' THEN sle.actual_qty ELSE 0 END), 0) AS undelivered,
                    COALESCE(SUM(CASE WHEN sle.warehouse = 'Goods In Transit - A' THEN sle.actual_qty ELSE 0 END), 0) AS goodsintransit
                FROM 
                    `tabItem` AS item
                LEFT JOIN 
                    `tabStock Ledger Entry` AS sle ON sle.item_code = item.item_code 
                     AND sle.is_cancelled = 0 
                     AND sle.voucher_type = 'Stock Entry'
                     AND item.import_file = '{import_file}'
            """

    stock_damage_result = frappe.db.sql(stock_damage_query, as_dict=True)
    qty = (stock_damage_result[0].damaged if stock_damage_result[0].damaged else 0) + (
        stock_damage_result[0].non_physical if stock_damage_result[0].non_physical else 0) + (
        stock_damage_result[0].undelivered if stock_damage_result[0].undelivered else 0) +(
        stock_damage_result[0].goodsintransit if stock_damage_result[0].goodsintransit else 0)
    amount = qty * avg_rate_with_lc

    return {
        'total_purchase_qty': round(total_purchase_qty, 2) if total_purchase_qty else 0,
        'total_sales_qty': round(total_sales_qty, 2) if total_sales_qty else 0,
        'total_balance_qty': round(total_balance_qty, 2) if total_balance_qty else 0,
        'avg_purchase_rate': round(avg_purchase_rate, 2) if avg_purchase_rate else 0,
        'avg_sale_rate': round(avg_sale_rate, 2) if avg_sale_rate else 0,
        'total_purchase_amount': round(total_purchase_amount, 2) if total_purchase_amount else 0,
        'total_sale_amount': round(total_sale_amount, 2) if total_sale_amount else 0,
        'total_lc_amount': round(total_lc_amount, 2) if total_lc_amount else 0,
        'total_cost': round(total_cost, 2) if total_cost else 0,
        'avg_rate_with_lc': round(avg_rate_with_lc, 2) if avg_rate_with_lc else 0,
        'balance_stock_value': round(balance_stock_value, 2) if balance_stock_value else 0,
        'cogs': (round(cogs, 2) if cogs else 0) + (round(amount, 2) if amount else 0),
        'profit_and_loss': round(profit_and_loss, 2) if profit_and_loss else 0,
        'qty': round(qty, 2) if qty else 0,
        'amount': round(amount, 2) if amount else 0,
        'damaged': stock_damage_result[0].damaged if stock_damage_result[0].damaged else 0,
        'non_physical': stock_damage_result[0].non_physical if stock_damage_result[0].non_physical else 0,
        'undelivered': stock_damage_result[0].undelivered if stock_damage_result[0].undelivered else 0,
        'goods_in_transit': stock_damage_result[0].goodsintransit if stock_damage_result[0].goodsintransit else 0

    }

    # ----------END----------
