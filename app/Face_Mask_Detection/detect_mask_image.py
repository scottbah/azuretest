from flask import Flask, render_template, flash, redirect, request, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from time import sleep


def detect_mask_images(UserInput):
    # load serialized face detector model
    prototxtPath = 'Face_Mask_Detection/face_detector/deploy.prototxt'
    weightsPath = 'Face_Mask_Detection/face_detector/res10_300x300_ssd_iter_140000.caffemodel'
    net = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model
    model = load_model('Face_mask_Detection/mask_detector.model')

    # load the input image, process it,  clone it, and grab the image spatial dimensions

    #convert string data to numpy array
    npimg = np.fromstring(UserInput, np.uint8)
    # convert numpy array to image
    image = cv2.imdecode(npimg,cv2.IMREAD_COLOR)

    (h, w) = image.shape[:2]

    # construct a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the face detections
    net.setInput(blob)
    detections = net.forward()

    maskCount = 0
    noMaskCount = 0
    # loop over the detections
    for i in range(detections.shape[2]):
    # extract the confidence (i.e., probability) associated with the detection
        confidence = detections[0, 0, i, 2]
    # filter out weak detections by ensuring the confidence is greater than the minimum confidence
        if confidence > 0.5:
        # compute the (x, y)-coordinates of the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # ensure the bounding boxes fall within the dimensions of the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # extract the face ROI, convert it from BGR to RGB channel ordering, resize it to 224x224, and preprocess it
            
            face = image[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)
            face = np.expand_dims(face, axis=0)

            # pass the face through the model to determine if the face has a mask or not
            (mask, withoutMask) = model.predict(face)[0]

            # determine the class label and color we'll use to draw the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            if label == "Mask":
                maskCount +=1
            elif label == "No Mask":
                noMaskCount +=1

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output frame
            cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
    
    if maskCount == 0 & noMaskCount == 0:
        rate = 0
    else:
        rate = (maskCount/(maskCount+noMaskCount))*100

    maskRate = "The mask wearing rate is: " + str(rate) + "%"
    cv2.putText(image, maskRate, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (122, 210, 245), 2)
    return image