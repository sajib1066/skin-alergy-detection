from django.views.generic import View, ListView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ultralytics import YOLO
from PIL import Image
import base64
from io import BytesIO
from PIL import Image
import os

from .allergy_categories import ALLERGY_TREATMENTS
from .models import ScanHistory

# Load your trained YOLOv11 model
model = YOLO("skin_alergy_detection/best.pt")

def normalize_label(label: str):
    label = label.lower()
    label = label.replace("pictures", "").replace("and related diseases", "")
    label = label.strip()

    # Optional: match known keywords from the dictionary
    for key in ALLERGY_TREATMENTS:
        if key in label:
            return key
    return label


class HomePageView(View):
    """ Home view """
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class ScanPageView(View):
    template_name = 'scan.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')
        camera_image_data = request.POST.get('camera_image')

        if camera_image_data:
            format, imgstr = camera_image_data.split(';base64,') 
            image = Image.open(BytesIO(base64.b64decode(imgstr)))
        elif image:
            image = Image.open(image)
        else:
            return render(request, self.template_name, {'error': 'No image provided.'})

        # Detection logic
        results = model(image)
        boxes = results[0].boxes
        if not boxes:
            return render(request, self.template_name, {'error': 'No allergy detected.'})

        detections = []
        for box in boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            normalized_label = normalize_label(label)
            treatment = ALLERGY_TREATMENTS.get(normalized_label.lower(), "Consult a doctor.")

            detection_data = {
                "allergy_type": normalized_label.title(),
                "confidence": float(box.conf[0]),
                "treatment": treatment
            }
            detections.append(detection_data)
            
            # Save to history if user is authenticated
            if request.user.is_authenticated:
                # Save image if it's a file upload
                saved_image = None
                if request.FILES.get('image'):
                    saved_image = request.FILES['image']
                
                ScanHistory.objects.create(
                    user=request.user,
                    image=saved_image,
                    allergy_type=detection_data["allergy_type"],
                    confidence=detection_data["confidence"],
                    treatment=detection_data["treatment"]
                )

        return render(request, self.template_name, {
            'detections': detections
        })


class HistoryView(LoginRequiredMixin, ListView):
    """View to display user's scan history"""
    model = ScanHistory
    template_name = 'history.html'
    context_object_name = 'scan_history'
    paginate_by = 10

    def get_queryset(self):
        return ScanHistory.objects.filter(user=self.request.user)
