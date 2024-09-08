# views.py

from django.http import JsonResponse, HttpResponse
import requests
import json


def sns_listener(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON payload
            sns_message = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Check the type of the SNS message
        message_type = sns_message.get("Type")

        if message_type == "SubscriptionConfirmation":
            # Confirm the subscription by visiting the SubscribeURL
            subscribe_url = sns_message.get("SubscribeURL")
            if subscribe_url:
                response = requests.get(subscribe_url)
                return JsonResponse(
                    {"message": "Subscription confirmed"}, status=200
                )
            else:
                return JsonResponse(
                    {"error": "No SubscribeURL found"}, status=400
                )

        elif message_type == "Notification":
            # Handle the notification message
            sns_message_body = sns_message.get("Message")
            print(f"Received notification: {sns_message_body}")
            return JsonResponse(
                {"message": "Notification received"}, status=200
            )

        else:
            # Unknown message type
            return JsonResponse({"error": "Unknown message type"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
