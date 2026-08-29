form_data = {
    "name": None,
    "age": None,
    "address": None,
    "phone": None
}


def update_form(new_data):
    for field in form_data:
        if form_data[field] is None and new_data.get(field) is not None:
            form_data[field] = new_data[field]

def correct_field(field, value):
    if field in form_data:
        form_data[field] = value

def show_form():
    print("\n----- FORM -----")

    for field, value in form_data.items():
        print(f"{field}: {value}")

    print("----------------")


def get_missing_fields():
    return [
        field
        for field, value in form_data.items()
        if value is None
    ]