import base64
import numpy as np
import cv2
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie  # Only use csrf_exempt for debugging!
from django.shortcuts import render

from . import utils

@csrf_exempt  # REMOVE this after you confirm CSRF works in production!
def receive_frame(request):
    if request.method == "POST":
        try:
            # Parse JSON payload
            try:
                data = json.loads(request.body.decode("utf-8"))
            except Exception as parse_e:
                return JsonResponse({"error": f"JSON decode error: {str(parse_e)}"}, status=400)

            img_data = data.get("image", "")
            lane_name = data.get("lane", "")
            if not img_data or "," not in img_data or not lane_name:
                return JsonResponse({"error": "Invalid or missing image/lane data"}, status=400)

            # Decode base64 image after comma (data:image/jpeg;base64,...)
            try:
                img_bytes = base64.b64decode(img_data.split(",")[1])
                np_arr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            except Exception as decode_e:
                return JsonResponse({"error": f"Image decode error: {str(decode_e)}"}, status=400)

            if frame is None:
                return JsonResponse({"error": "Could not decode image"}, status=400)

            # Process frame for specific lane using your custom logic
            try:
                result = utils.process_frame_for_lane(frame, lane_name)
            except Exception as process_e:
                return JsonResponse({"error": f"Processing error: {str(process_e)}"}, status=500)

            # Return your result dictionary (must be JSON-serializable)
            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

@ensure_csrf_cookie
def traffic_dashboard(request):
    """Render your live.html dashboard."""
    return render(request, 'live.html')

def about(request):
    """Render your about.html page."""
    return render(request, 'about.html')

def home(request):
    """Render your dashboard.html page."""
    return render(request, 'dashboard.html')
