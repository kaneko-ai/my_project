medical_glossary = {
    "CD73": "細胞表面にある酵素で、免疫反応やがんに関与します。",
    "PD-1": "免疫チェックポイントの一種で、がん免疫療法に関係します。",
    "EGFR": "がんの増殖に関与する遺伝子の一つです。"
}

def annotate_medical_terms(text):
    for term, desc in medical_glossary.items():
        tooltip = f"<span title='{desc}' style='border-bottom:1px dotted #000; cursor:help;'>{term}</span>"
        text = text.replace(term, tooltip)
    return text
