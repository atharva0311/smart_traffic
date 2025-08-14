import base64
import numpy as np
import cv2
from django.http import JsonResponse # type: ignore
import json
from . import utils
from django.views.decorators.csrf import ensure_csrf_cookie # type: ignore
from django.shortcuts import render # type: ignore


def receive_frame(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            img_data = data.get("image", "")
            lane_name = data.get("lane", "")

            if not img_data or "," not in img_data or not lane_name:
                return JsonResponse({"error": "Invalid or missing image/lane data"}, status=400)

            # Decode base64 image after comma (data:image/jpeg;base64,...)
            img_bytes = base64.b64decode(img_data.split(",")[1])
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"error": "Could not decode image"}, status=400)

            # Process frame for specific lane
            result = utils.process_frame_for_lane(frame, lane_name)
            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@ensure_csrf_cookie
def traffic_dashboard(request):
    """Render your index.html dashboard."""
    return render(request, 'live.html')

def about(request):
    """Render your index.html dashboard."""
    return render(request, 'about.html')

def home(request):
    """Render your index.html dashboard."""
    return render(request, 'dashboard.html')

