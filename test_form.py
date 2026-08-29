from form_manager import update_form, show_form, get_missing_fields


# First answer
data_from_ai = {
    "name": "Atharva",
    "age": 18,
    "address": None,
    "phone": None
}

update_form(data_from_ai)

show_form()


# Second answer
data_from_ai = {
    "name": None,
    "age": None,
    "address": "Vellore",
    "phone": None
}

update_form(data_from_ai)

show_form()


print("\nMissing fields:")
print(get_missing_fields())