import xml.etree.ElementTree as ET

def create_word_table(table_data, border=None, row_borders=None, caption=None):
    NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    def w(tag): return f"{{{NS['w']}}}{tag}"
    ET.register_namespace("w", NS["w"])
    elements = []
    # Optional: Add a caption paragraph
    if caption:
        p = ET.Element(w("p"))
        pPr = ET.SubElement(p, w("pPr"))
        ET.SubElement(pPr, w("pStyle"), {w("val"): "Caption"})
        r = ET.SubElement(p, w("r"))
        t = ET.SubElement(r, w("t"))
        t.text = caption
        elements.append(p)
    tbl = ET.Element(w("tbl"))
    # Table properties
    tblPr = ET.SubElement(tbl, w("tblPr"))
    ET.SubElement(tblPr, w("tblStyle"), {w("val"): "TableNormal"})
    ET.SubElement(tblPr, w("tblW"), {w("w"): "0", w("type"): "auto"})
    if border:
        tblBorders = ET.SubElement(tblPr, w("tblBorders"))
        for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            ET.SubElement(tblBorders, w(side), {
                w("val"): "single",
                w("sz"): str(border.get("size", 4)),
                w("color"): border.get("color", "000000")
            })
    # Calculate column count
    max_cols = 0
    for row in table_data:
        count = 0
        for cell in row:
            colspan = cell.get("colspan", 1) if isinstance(cell, dict) else 1
            count += colspan
        max_cols = max(max_cols, count)
    # Add table grid
    tblGrid = ET.SubElement(tbl, w("tblGrid"))
    col_width = str(2400)
    for _ in range(max_cols):
        ET.SubElement(tblGrid, w("gridCol"), {w("w"): col_width})
    rowspan_tracker = {}
    for row_idx, row in enumerate(table_data):
        tr = ET.SubElement(tbl, w("tr"))
        row_border = row_borders.get(row_idx, {}) if row_borders else {}
        col_idx = 0
        while col_idx < max_cols:
            if (row_idx, col_idx) in rowspan_tracker:
                tc = ET.SubElement(tr, w("tc"))
                tcPr = ET.SubElement(tc, w("tcPr"))
                ET.SubElement(tcPr, w("vMerge"), {w("val"): "continue"})
                ET.SubElement(tcPr, w("tcW"), {w("w"): col_width, w("type"): "dxa"})
                col_idx += 1
                continue
            if not row:
                break
            cell = row.pop(0)
            text = cell if isinstance(cell, str) else cell.get("text", "")
            color = None
            colspan = 1
            rowspan = 1
            if isinstance(cell, dict):
                color = cell.get("color")
                colspan = cell.get("colspan", 1)
                rowspan = cell.get("rowspan", 1)
            if rowspan > 1:
                for i in range(1, rowspan):
                    rowspan_tracker[(row_idx + i, col_idx)] = True
            tc = ET.SubElement(tr, w("tc"))
            tcPr = ET.SubElement(tc, w("tcPr"))
            ET.SubElement(tcPr, w("tcW"), {w("w"): str(2400 * colspan), w("type"): "dxa"})
            if colspan > 1:
                ET.SubElement(tcPr, w("gridSpan"), {w("val"): str(colspan)})
            if rowspan > 1:
                ET.SubElement(tcPr, w("vMerge"), {w("val"): "restart"})
            if color:
                ET.SubElement(tcPr, w("shd"), {
                    w("val"): "clear", w("color"): "auto", w("fill"): color
                })
            if row_border:
                tcBorders = ET.SubElement(tcPr, w("tcBorders"))
                for side, b in row_border.items():
                    ET.SubElement(tcBorders, w(side), {
                        w("val"): "single",
                        w("sz"): str(b.get("size", 4)),
                        w("color"): b.get("color", "000000")
                    })
            p = ET.SubElement(tc, w("p"))
            r = ET.SubElement(p, w("r"))
            t = ET.SubElement(r, w("t"))
            t.text = text
            col_idx += colspan
    elements.append(tbl)
    # Wrap in root element if needed
    root = ET.Element("root")
    for el in elements:
        root.append(el)
    return ET.tostring(root, encoding="unicode")


table_data = [
    [{"text": "Header", "colspan": 3, "color": "DDD9C4"}],
    [{"text": "A", "rowspan": 2}, "B", "C"],
    ["D", "E"],
    ["F", "G", "H"]
]

border = {"size": 8, "color": "000000"}
row_borders = {
    1: {"bottom": {"size": 12, "color": "FF0000"}},
    3: {"top": {"size": 6, "color": "0000FF"}}
}
caption = "Table 1: Example with Row and Cell Styling"

xml = create_word_table(table_data, border=border, row_borders=row_borders, caption=caption)
print(xml)

