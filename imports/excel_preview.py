from openpyxl import load_workbook

def preview_excel_import(file_path):
    print("Opening Excel workbook...")

    workbook = load_workbook(
        file_path,
        data_only=True,
        read_only=True,
        keep_links=False,
    )

    print("Excel workbook opened.")

    sheet = workbook.active

    preview = {
        "category": sheet["C1"].value,
        "class": sheet["C2"].value,
        "type": sheet["C3"].value,
        "event": sheet["C4"].value,
        "date": sheet["C5"].value,
        "time": sheet["C6"].value,
        "market": sheet["C7"].value,
        "selections": []
    }

    row = 10

    while True:
        selection = sheet[f"A{row}"].value
        price = sheet[f"B{row}"].value

        if selection is None:
            break

        preview["selections"].append({
            "name": selection,
            "price": price
        })

        row += 1

    workbook.close()

    print("Excel preview complete.")

    return preview