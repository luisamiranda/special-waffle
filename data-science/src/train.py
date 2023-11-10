#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import Lock
from train import wrap_callbacks, specialize_training_spec
from ultralytics import YOLO
import argparse
import mlflow
import os

LOCK = Lock()


def main():
    print(f"Current Dir Start: {os.getcwd()}")
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--labeled_images", type=str, help="Path to image folder")
    parser.add_argument("--trained_model", type=str, help="Path to trained model")
    parser.add_argument("--experiment_name", type=str, help="Name of experiment")
    parser.add_argument("--datasets", type=str, help="Comma-separated array of datasets")

    args = parser.parse_args()

    # Local Debugging:
    #
    # import debugpy
    # debugpy.listen(5678)
    # debugpy.wait_for_client()
    # input("Press Enter to continue...")

    # Set environment for training
    PROJECT = args.experiment_name
    os.environ["MLFLOW_EXPERIMENT"] = f"/Shared/{PROJECT}"

    # get the data definition file
    data_def = "./data-science/src/train/custom-coco.yaml"
    with open(data_def, "r") as handle:
        fq_data_def = os.path.abspath(data_def)

    # replace placeholders in the data definition file with specific values
    specialize_training_spec(fq_data_def, args.labeled_images, "yolov8-train")

    # set current working directory to the output folder
    # This is required because the YOLO model is very specific about folder structure and
    # uses the "current directory" as root for some of its operations
    os.chdir(args.trained_model)

    with mlflow.start_run():
        _model = YOLO("yolov8n.yaml")  # Here we select the model to train
        model = wrap_callbacks(
            # Here we add a wrapper for all the callbacks to ensure logging thread safety
            _model,
            lock=LOCK,
        )

        try:
            model.train(
                # Here we train
                data=fq_data_def,
                epochs=2,
                imgsz=640,
                project=PROJECT,
            )

        except Exception as e:
            # TODO: IMPROVE ERROR HANDLING AND LOGGING
            print(f"Current Dir in except: {os.getcwd()}")
            print("Unexpected error:")
            print(e)
            raise e
        finally:
            mlflow.end_run()

if __name__ == "__main__":
    main()
