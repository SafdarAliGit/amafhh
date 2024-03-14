import frappe


@frappe.whitelist()
def make_non_physical_stock_entry(posting_date,name,source_warehouse,source_item_code,weight_difference,rate):
    # STOCK ENTRY SAVING
    doc = frappe.new_doc("Stock Entry")
    doc.stock_entry_type = "Material Transfer"
    doc.purpose = "Material Transfer"
    doc.posting_date = posting_date
    doc.roll_to_roll_conversion = name
    source_warehouse = source_warehouse

    # Append source item
    it = doc.append("items", {})
    it.set_basic_rate_manually = 1
    it.s_warehouse = source_warehouse
    it.t_warehouse = 'Non Fisical Damage - A'
    it.item_code = source_item_code
    it.qty = weight_difference
    it.basic_rate = rate
    it.amount = float(rate) * float(weight_difference)

    try:
        # doc.ignore_validation = True
        doc.submit()
        rtrc = frappe.get_doc("Roll To Roll Conversion", name)
        rtrc.non_physical_stock_entry = 1
        rtrc.save()
    except Exception as e:
        frappe.throw(frappe._("Error submitting Stock Entry: {0}".format(str(e))))
