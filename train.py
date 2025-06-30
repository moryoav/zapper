#!/usr/bin/env python3
"""
train.py
--------

Fine-tunes a MobileNet-V2 96×96 classifier on the dataset/*
and exports a quantised mosquito.tflite model.
"""

from tflite_model_maker import image_classifier
from tflite_model_maker.image_classifier import DataLoader
from pathlib import Path

PATCH_SIZE = 96
EPOCHS     = 10
BATCH_SIZE = 32

DATA_DIR   = Path("dataset")
EXPORT_DIR = Path("export")
EXPORT_DIR.mkdir(exist_ok=True)

def main():
    data = DataLoader.from_folder(str(DATA_DIR))
    train, test = data.split(0.9)

    spec = image_classifier.ModelSpec(uri="mobilenet_v2_100_96")
    model = image_classifier.create(
        train,
        model_spec=spec,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=test
    )

    loss, acc = model.evaluate(test)
    print(f"\nValidation accuracy: {acc:.3f}")

    model.export(
        EXPORT_DIR,
        tflite_filename="mosquito.tflite",
        quantization_config=image_classifier.QuantizationConfig.for_int8()
    )
    print("✓ Model saved in", EXPORT_DIR.resolve())

if __name__ == "__main__":
    main()
