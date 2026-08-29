from form_manager import update_form, show_form, get_missing_fields


while True:

    print("\nCurrent form:")
    show_form()

    missing = get_missing_fields()

    if not missing:
        print("\nForm completed!")
        break

    next_field = missing[0]

    print(f"\nPlease provide your {next_field}.")

    user_input = input("You: ")

    # For now, we will manually simulate AI extraction
    data = {
        "name": None,
        "age": None,
        "address": None,
        "phone": None
    }

    if next_field == "name":
        data["name"] = user_input

    elif next_field == "age":
        data["age"] = int(user_input)

    elif next_field == "address":
        data["address"] = user_input

    elif next_field == "phone":
        data["phone"] = user_input

    update_form(data)