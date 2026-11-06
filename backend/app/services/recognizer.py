# =========================================================
# app/services/recognizer.py
# Image classification service
# =========================================================

import os
import random
from pathlib import Path

from app import db
from app.models import ItemClass


class Recognizer:
    """
    Image recognizer.
    - If a trained model exists at config.MODEL_PATH, use it (PyTorch).
    - Otherwise, return a MOCK prediction so the frontend works end-to-end.
    """

    def __init__(self, model_path=None):
        self.model = None
        self.classes = []
        self.model_loaded = False

        if model_path and os.path.exists(model_path):
            self._load_model(model_path)

    # ---------- Load real model ----------
    def _load_model(self, model_path):
        try:
            import torch
            import torchvision.transforms as T
            from torchvision import models

            checkpoint = torch.load(model_path, map_location='cpu')
            self.classes = checkpoint['classes']

            num_classes = len(self.classes)
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
            model.load_state_dict(checkpoint['model_state'])
            model.eval()

            self.model = model
            self.transform = T.Compose([
                T.Resize(224),
                T.CenterCrop(224),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225]),
            ])
            self.model_loaded = True
            print(f'✅ Recognizer loaded ({num_classes} classes)')
        except Exception as e:
            print(f'⚠️  Could not load model: {e}')
            self.model = None
            self.model_loaded = False

    # ---------- Predict ----------
    def predict(self, image_path):
        """
        Returns: (class_name, confidence)
        - If model loaded: real prediction
        - Otherwise: mock prediction (for dev)
        """
        if self.model_loaded:
            return self._predict_real(image_path)
        return self._predict_mock()

    # ---------- Real prediction ----------
    def _predict_real(self, image_path):
        import torch
        from PIL import Image

        img = Image.open(image_path).convert('RGB')
        tensor = self.transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence, idx = torch.max(probs, 0)

        class_name = self.classes[idx.item()]
        return class_name, float(confidence.item())

    # ---------- Mock prediction ----------
    def _predict_mock(self):
        """Random prediction — for development without trained model."""
        available = ItemClass.query.all()
        if not available:
            return None, 0.0

        # Mostly pick a high confidence (for a satisfying demo)
        chosen = random.choice(available)
        # 80% chance of success, 20% chance of low confidence
        if random.random() < 0.80:
            confidence = random.uniform(0.80, 0.98)
        else:
            confidence = random.uniform(0.30, 0.70)

        return chosen.class_name, confidence


# ---------- Singleton ----------
_recognizer_instance = None

def get_recognizer(model_path=None):
    """Lazy singleton — loads the model once."""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = Recognizer(model_path)
    return _recognizer_instance