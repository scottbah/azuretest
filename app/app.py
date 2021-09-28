from flask import Flask, render_template, redirect, request, url_for, Response
import cv2
from PIL import Image
import io
import base64
import pafy
from tensorflow.keras.models import load_model
from Face_Mask_Detection.detect_mask_image import detect_mask_images
from Face_Mask_Detection.detect_mask_video import detect_and_predict_mask
prototxtPath = 'Face_Mask_Detection/face_detector/deploy.prototxt'
weightsPath = 'Face_Mask_Detection/face_detector/res10_300x300_ssd_iter_140000.caffemodel'
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model('Face_Mask_Detection/mask_detector.model')


app = Flask(__name__, static_folder= 'static')
app.secret_key = 'supersecretpwd'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ClassifyImage', methods=['GET', 'POST'])
def ClassifyImage():
    return render_template('ClassifyImage.html')

###FOR CLASSIFYING IMAGES, IMPLEMENT FILE CHECKING, ONLY ACCEPTABLE FILE TYPES SUCH AS JPG, PNG, ETC WILL BE ALLOWED. 
@app.route('/ClassifiedImage', methods=['GET', 'POST'])
def ClassifiedImage():
    if request.method == 'POST':
        #read image file string data
        file = request.files['InputImage'].read()

        #Run mask detection model on user input
        image = detect_mask_images(file)

        #Flip cv2 RGB values from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #Convert numpy array into a PIL image
        image = Image.fromarray(image.astype('uint8'))

        data = io.BytesIO()

        image.save(data, 'PNG')

        encoded_img_data = base64.b64encode(data.getvalue())

        return render_template('ClassifiedImage.html', img_data=encoded_img_data.decode('utf-8'))

@app.route('/ClassifyVideo', methods=['GET', 'POST'])
def ClassifyVideo():
    return render_template('ClassifyVideo.html')

@app.route('/ClassifiedWebcam', methods=['GET', 'POST'])
def ClassifiedWebcam():
    return render_template('ClassifiedWebcam.html')

@app.route('/ClassifiedIPCamera', methods=['GET', 'POST'])
def ClassifiedIPCamera():
    return render_template('ClassifiedIPCamera.html')

@app.route('/ClassifiedVideo', methods=['GET', 'POST'])
def ClassifiedVideo():
    return render_template('ClassifiedVideo.html')

@app.route('/ClassifiedLink', methods=['GET', 'POST'])
def ClassifiedLink():
    #Handle the POST request. This is called after the user submits the youtube video they wish to classify.
    #Form POST input is changed to URL Safe Base64 as to not introduce escape characters when moving the data between ClassifiedLink and video_link
    if request.method == 'POST':
        message = request.form.get('UserURL')
        message_bytes = message.encode('ascii')
        base64_bytes = base64.urlsafe_b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return render_template('ClassifiedLink.html', x = base64_message)

    #Otherwise, handle the GET request
    return render_template('Select_link.html')

@app.route('/peopleDensity')
def peopleDensity():
    return render_template('peopleDensity.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/forgotPassword')
def forgotPassword():
    return render_template('forgotPassword.html')

@app.route('/typeSelectMask', methods=['GET', 'POST'])
def typeSelectMask():
    return render_template('typeSelectMask.html')


def gen_frames(camera):  # generate frame by frame from camera
    ####DOES NOT WORK WITHIN DOCKER ATM
   while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        try:
            (locs, preds) = detect_and_predict_mask(frame,  faceNet, maskNet)
        except Exception:
            pass

        maskCount = 0
        noMaskCount = 0

        for (box, pred) in zip(locs, preds):

            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            # determine the class label and color we'll use to draw the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            if label == "Mask":
                maskCount += 1
            elif label == "No Mask":
                noMaskCount += 1

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output frame
            cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        if maskCount == 0 & noMaskCount == 0:
            rate = 0
        else:
            rate = (maskCount/(maskCount+noMaskCount))*100

        maskRate = "The mask wearing rate is: " + str(rate) + "%"
        cv2.putText(frame, maskRate, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (122, 210, 245), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed_webcam')
def video_feed_webcam():
    return Response(gen_frames(cv2.VideoCapture(0)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_link/<base64_message>', methods=['GET', 'POST'])
def video_link(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.urlsafe_b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    url = str(message)
    video = pafy.new(message)
    play = video.getbest(preftype="mp4")
    return Response(gen_frames(cv2.VideoCapture(play.url)), mimetype='multipart/x-mixed-replace; boundary=frame')


#Start the web server.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
