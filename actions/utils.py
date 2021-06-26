def convert_number(slot_value):
    if "٠" in slot_value:
        slot_value = slot_value.replace("٠", "0")
    if "١" in slot_value:
        slot_value = slot_value.replace("١", "1")
    if "٢" in slot_value:
        slot_value = slot_value.replace("٢", "2")
    if "٣" in slot_value:
        slot_value = slot_value.replace("٣", "3")
    if "٤" in slot_value:
        slot_value = slot_value.replace("٤", "4")
    if "٥" in slot_value:
        slot_value = slot_value.replace("٥", "5")
    if "٦" in slot_value:
        slot_value = slot_value.replace("٦", "6")
    if "٧" in slot_value:
        slot_value = slot_value.replace("٧", "7")
    if "٨" in slot_value:
        slot_value = slot_value.replace("٨", "8")
    if "٩" in slot_value:
        slot_value = slot_value.replace("٩", "9")

    return slot_value


if __name__ == '__main__':
    print(convert_number("٠٦٨"))
