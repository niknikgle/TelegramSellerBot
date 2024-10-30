import requests
import json

import database
import config
import server

auth_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
client_id = (
    "AXMbC4H6n-ZQHbFKam-CW5I-TN-TFSw5jEPdwhvg50HlOW_OCYf45uuuk6mrGUfqy4GO36Q7sdaq7YTG"
)
secret = (
    "EBeLEc_GQKcAtPCOuIRVbw6n9_KfyWQYSfbesy5_FJfTk2deMTNQVlw44xMvIamBbrbnDJkX_ERLUa4e"
)


def create_access_token():
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }

    data = {"grant_type": "client_credentials"}

    # Get the token
    response = requests.post(
        auth_url, headers=headers, data=data, auth=(client_id, secret)
    )

    if response.status_code != 200:
        raise Exception("Failed to obtain token: ", response.json())

    access_token = response.json()["access_token"]
    return access_token


def create_invoice(amount):
    print(amount)

    # Step 2: Create an order
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {create_access_token()}",
    }

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "items": [
                    {
                        "name": "Account_Example",
                        "description": "Desc Example",
                        "quantity": "1",
                        "unit_amount": {"currency_code": "USD", "value": amount},
                    }
                ],
                "amount": {
                    "currency_code": "USD",
                    "value": amount,
                    "breakdown": {
                        "item_total": {"currency_code": "USD", "value": amount}
                    },
                },
            }
        ],
        "application_context": {
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel",
        },
    }

    # Send the request to create an order
    response = requests.post(url, headers=headers, data=json.dumps(order_data))

    order_response = response.json()

    if response.status_code != 201:
        print("Order creation failed")
        print(order_response)
    else:
        order_id = order_response["id"]
        print(f"Order ID: {order_id}")

        # Extract the approval link for the buyer
        approval_url = None
        for link in order_response["links"]:
            if link["rel"] == "approve":
                approval_url = link["href"]
                break

        if approval_url:
            print(f"Buyer approval link: {approval_url}")
            return [approval_url, order_id]
            # You should now redirect the buyer to this URL
        else:
            print("No approval link found in the response")


def check_paypal_payment(user_id, order_id, amount):
    print(f"started paypal checking: {str(order_id)}")

    # Step 1: Set up headers, including Authorization
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {create_access_token()}",  # Ensure the token is added here
    }

    # Step 2: PayPal capture endpoint
    capture_url = (
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
    )

    # Step 3: Post request to capture the order
    capture_response = requests.post(capture_url, headers=headers)

    try:
        capture_data = capture_response.json()
    except ValueError:
        print("FAIL - Invalid JSON response")
        return f"{order_id} : Failed ❌ - Invalid response format"

    # Step 4: Check the status of the capture
    if capture_response.status_code == 201:  # Adjusted status code check to 200
        status = capture_data.get("status")
        if status == "COMPLETED":

            database.add_balance(address=server.request(user_id), value_coin=amount)
            return f"{order_id} : Success ✅"
        else:
            print(f"FAIL - Status: {status}")
            return f"{order_id} : Failed ❌ - Status: {status}"
    else:
        print(f"FAIL - Capture failed with status code {capture_response.status_code}")
        print(f"Response: {capture_data}")
        return f"{order_id} : Failed ❌ - Capture failed"
