
import frappe

def update_item_weight(doc, method):
    doc.custom_weight_per_unit = calculate_unit_weight(doc)
    

def calculate_unit_weight(doc):
    weight_factor = 0
    single_ream_pkt_weight = 0

    conversion_type = doc.item_group or ""
    width = float(doc.width or 0)
    gsm = float(doc.gsm or 0)
    length = float(doc.length or 0)

    if conversion_type == "REAM":
        weight_factor = 3100
        single_ream_pkt_weight = (width * gsm * length) / weight_factor

    elif conversion_type == "PKT":
        weight_factor = 15500
        single_ream_pkt_weight = (width * gsm * length) / weight_factor

    else:
        single_ream_pkt_weight = 0

    return single_ream_pkt_weight



