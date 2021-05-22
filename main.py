from flask import Flask, jsonify, send_file
from flask_restful import Api, Resource
from datetime import datetime


# import cv2
# from tensorflow.keras import models
# import pickle
# import numpy as np

# ML Section
def get_frame(video_path, hour=0, minute=0, second=0):
    video=cv2.VideoCapture(video_path)

    total_frame=video.get(cv2.CAP_PROP_FRAME_COUNT)
    framerate=video.get(cv2.CAP_PROP_FPS)

    hour=abs(hour)
    minute=abs(minute)
    second=abs(second)

    intented_frame= int((hour*3600+minute*60+second)*framerate)

    if intented_frame==0:
        intented_frame=1
    if intented_frame>total_frame:
      return 0

    video.set(1, intented_frame)
    ret, frame = video.read()
    return frame

def load_model(model_path):
  model = models.load_model(model_path)
  return model

def load_box(box_path):
  file = open(box_path, 'rb')
  coordinates = pickle.load(file)
  file.close()
  return coordinates

def predict(frame, model, coordinates):
  frame_bersih = frame.copy()
  empty = 0

  for i in range(len(coordinates)):
    points = coordinates[i]
    x,y,w,h = cv2.boundingRect(points)
    crop = frame[y:y+h, x+1:x+w]

    test = cv2.resize(crop, (300,300))
    test = np.expand_dims(test, axis=0)
    pred = model.predict(test)

    if (pred < 0.9):
      empty += 1
      points = coordinates[i].reshape((-1, 1, 2))
      frame_bersih = cv2.polylines(frame_bersih, [points], True, color=(0,255,0), thickness=2)
  
  height = frame_bersih.shape[1]
  frame_bersih = frame_bersih[50:y+height, :]
  return empty, frame_bersih


#END SECTION

#model = load_model('model/vgg16.h5')

def get_time():
    now = datetime.now()
    return now.hour, now.minute, now.second

def get_day(hour):
    if hour > 18 or hour < 5:
        return "malem"
    elif hour < 9:
        return "pagibanget"
    elif hour < 11:
        return "pagisedang"
    elif hour < 14:
        return "siang"
    elif hour < 16:
        return "soresedang"
    else:
        return "sorebanget"


app = Flask(__name__)
api = Api(app)

#IN-MEMORY DATASTORE
locations = {
    "polrestabdl": {
        "name": "Polresta Bandar Lampung",
        "address": "Jl. Mayjen MT Haryono, Gotong Royong, Kec. Tj. Karang Pusat, Kota Bandar Lampung, Lampung 35119",
        "description": "Kantor Polresta Provinsi Bandar Lampung melayani laporan & pengaduan masyarakat. Buka 07.00-14.30.",
        "available_spot": 37,
        "cctv_url": "https://rtsp.me/embed/y4z3haiE/"
    },

    "plazasenayan": {
        "name": "Plaza Senayan",
        "address": "Jl. Asia Afrika No.8, Gelora, Kec. Tanah Abang, Kota Jakarta Pusat, Daerah Khusus Ibukota Jakarta 10270",
        "description": "Plaza Senayan menghadirkan pusat perbelanjaan dari berbagai merek ternama khususnya pakaian, fashion, dan restoran cepat saji. Buka 10.00-21.00",
        "available_spot": 152,
        "cctv_url": "https://rtsp.me/embed/y4z3haiE/"
    },

    "sekolahplth": {
        "name": "Sekolah Pelita Harapan",
        "address": "Jl. Boulevard Palem Raya No.2500, Klp. Dua, Kec. Klp. Dua, Tangerang, Banten 15810",
        "description": "Sekolah Pelita Harapan adalah sekolah internasional swasta dengan lima lokasi strategis di Jakarta. Buka 07.00-15.30",
        "available_spot": 80,
        "cctv_url": "https://rtsp.me/embed/y4z3haiE/"
    }
}


# ROUTING
class Locations(Resource):
    def get(self):
        names = []

        for location in locations:
            info = locations[location]
            names.append(info.get("name"))
        
        response = {"status": "success", "data": names}
        return jsonify(response)

class PlaceInformation(Resource):
    def get(self, name):
        
        #hour, minute, second = get_time()

        #daytime = get_day(int(hour))

        #video_path = 'videos/' + daytime

        #frame = get_frame(video_path, hour = 0, minute % 4, second)
        #coordinates = load_box('coordinates/polrestabdl.pkl')
        #locations[name][available_spot], _ = predict(frame, model, coordinates)

        response = {"status": "success", "data": locations[name]}
        return jsonify(response)

#BASE URL: https://project-id.appspot.com
api.add_resource(Locations, "/locations")      
api.add_resource(PlaceInformation, "/location/<string:name>")





if __name__ == "__main__" :
    app.run(debug = True)


#TO-DO LIST
#1. Configure requirements, file .pkl, .h5, .mp5 ke Cloud Storage Bucket (2 days)
#2. Deploy & Configure ke App Engine (3 days)