import csv

def preview_event_csv(file_path):

    with open(file_path, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        print()
        print("CSV PREVIEW")
        print("===========")
        print()

        for row in reader:

            print(row)

def validate_event_csv(file_path, platform):

    required_columns = [
        "Category",
        "Class",
        "Type",
        "Event",
        "Market",
        "Selection",
        "Price"
    ]

    with open(file_path, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        missing = [
            column
            for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing:

            print()
            print("CSV VALIDATION FAILED")
            print("=====================")

            for column in missing:
                print(f"Missing column: {column}")

            return False
        
        valid_categories = get_valid_categories(platform)
        valid_classes = get_valid_classes(platform)
        valid_types = get_valid_types(platform)

        for row_number, row in enumerate(reader, start=2):

            if row["Category"] not in valid_categories:

                print(
                    f"❌ Row {row_number}: Invalid category '{row['Category']}'"
                )

                return False
            
            if row["Class"] not in valid_classes:

                print(
                    f"❌ Row {row_number}: Invalid class '{row['Class']}'"
                )

                return False


            if row["Type"] not in valid_types:

                print(
                    f"❌ Row {row_number}: Invalid type '{row['Type']}'"
                )

                return False
            
            if event_exists(platform, row):

                print()
                print(f"⚠ Possible duplicate on row {row_number}")
                print(f"Event: {row['Event']}")

        print()
        print("✓ CSV structure valid.")

        return True
    
def get_valid_categories(platform):

    categories = set()

    for event in platform:
        categories.add(event["category"])

    return sorted(categories)

def get_valid_classes(platform):

    classes = set()

    for event in platform:
        classes.add(event["class"])

    return sorted(classes)

def get_valid_types(platform):

    types = set()

    for event in platform:
        types.add(event["type"])

    return sorted(types)

def event_exists(platform, row):

    for event in platform:

        if (
            event["category"] == row["Category"]
            and event["class"] == row["Class"]
            and event["type"] == row["Type"]
            and event["event_name"] == row["Event"]
        ):

            return True

    return False

from event_functions import create_event
from save_load import save_platform
from client_save_load import save_clients
from audit_functions import add_audit_log

def import_event_markets_from_csv(file_path, platform, clients):

    if not validate_event_csv(file_path, platform):

        print()
        print("Import cancelled.")

        return

    created_events = 0
    created_markets = 0
    created_selections = 0

    with open(file_path, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            event = None

            for existing_event in platform:

                if (
                    existing_event["category"] == row["Category"]
                    and existing_event["class"] == row["Class"]
                    and existing_event["type"] == row["Type"]
                    and existing_event["event_name"] == row["Event"]
                ):

                    event = existing_event

            if event is None:

                event = create_event(
                    row["Category"],
                    row["Class"],
                    row["Type"],
                    row["Event"]
                )

                platform.append(event)

                created_events += 1

                for client in clients:

                    if row["Category"] in client.get("subscriptions", []):

                        if row["Event"] not in client["booked_events"]:

                            client["booked_events"].append(row["Event"])

            market = None

            for existing_market in event["markets"]:

                if existing_market["name"] == row["Market"]:

                    market = existing_market

            if market is None:

                market = {
                    "name": row["Market"],
                    "selections": [],
                    "status": "Trading",
                    "published": False,
                    "limits": {
                        "max_win_per_customer": 500,
                        "max_liability": 5000
                    },
                    "notes": ""
                }

                event["markets"].append(market)

                created_markets += 1

            selection = {
                "name": row["Selection"],
                "price": [
                    int(row["Price"].split("/")[0]),
                    int(row["Price"].split("/")[1])
                ],
                "pending_price": None,
                "active": True,
                "displayed": True,
                "price_history": []
            }

            market["selections"].append(selection)

            created_selections += 1

            add_audit_log(
                f"CSV import added {row['Selection']} to {row['Event']} - {row['Market']}"
            )

    save_platform(platform)
    save_clients(clients)

    print()
    print(f"✓ Events created: {created_events}")
    print(f"✓ Markets created: {created_markets}")
    print(f"✓ Selections created: {created_selections}")