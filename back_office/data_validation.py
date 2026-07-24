def validate_platform(platform):

    issues = []

    for event in platform:

        event_name = event.get("event_name", "Unnamed Event")

        if event.get("event_name", "") == "":
            issues.append("Event missing name")

        if len(event.get("markets", [])) == 0:
            issues.append(f"{event_name} has no markets")

        for market in event.get("markets", []):

            market_name = market.get("name", "Unnamed Market")

            if market.get("name", "") == "":
                issues.append(f"{event_name} has market missing name")

            selections = market.get("selections", [])

            if len(selections) == 0:
                issues.append(f"{event_name} > {market_name} has no selections")

            seen_names = []

            for selection in selections:

                selection_name = selection.get("name", "Unnamed Selection")

                if selection.get("name", "") == "":
                    issues.append(f"{event_name} > {market_name} has selection missing name")

                if "price" not in selection:
                    issues.append(f"{event_name} > {market_name} > {selection_name} has no price")

                if selection_name in seen_names:
                    issues.append(f"{event_name} > {market_name} has duplicate selection: {selection_name}")

                seen_names.append(selection_name)

    return issues


def display_validation(platform):

    print()
    print("=" * 50)
    print("DATA VALIDATION")
    print("=" * 50)
    print()

    issues = validate_platform(platform)

    if len(issues) == 0:

        print("✅ No validation issues found.")

    else:

        print(f"⚠️ {len(issues)} issue(s) found:")
        print()

        for issue in issues:
            print(f"- {issue}")

    input("\nPress Enter...")