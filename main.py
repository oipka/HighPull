import time
import cv2
import numpy as np
from PIL import Image
from flask import Flask, render_template, url_for, Response, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import folium


from database_setup import Base, Auto, Camera, Check_Map
from detection import VideoCamera

app = Flask(__name__)


engine = create_engine('sqlite:///auto.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/', defaults={'width': None, 'height': None})
@app.route('/<width>/<height>', methods=['GET', 'POST'])
def index(width=None, height=None):
    if not width or not height:
        return """
            <script>
            (() => window.location.href = window.location.href +
            ['', window.innerWidth, window.innerHeight].join('/'))()
            </script>
            """
    print(width)
    return render_template("index.html", width=width, height=height)

@app.route('/camera', methods=['GET', 'POST'])
def camera():
    if request.method == 'POST':
        if request.form.get('add') == 'add':
            newCamera = Camera(name=request.form['name'], koord=request.form['koord'])
            session.add(newCamera)
            session.commit()
        else:
            delCamera = session.query(Camera).filter_by(id=request.form['delete']).one()
            session.delete(delCamera)
            session.commit()
    camers = session.query(Camera).all()
    return render_template('camera.html', camers=camers)

@app.route('/map', methods=['GET', 'POST'])
def map():
    start_coords = (45.09789580993381, 38.97959809302496)
    folium_map = folium.Map(location=start_coords, zoom_start=13)
    if request.method == 'POST':
        loc = []
        for i in session.query(Check_Map).filter_by(number = request.form['number']):
            a = tuple([float(i.koord) for i.koord in i.koord.split(', ')])
            loc.append(a)
            folium.Marker(a, popup=i.time, ).add_to(folium_map)
        session.rollback()
        folium.PolyLine(loc,
                        color='red',
                        weight=15,
                        opacity=0.8).add_to(folium_map)
        # for i in range(len(loc)):
        #     folium.Marker(loc[i], popup="Mt. Hood Meadows",).add_to(folium_map)
    folium_map.save('templates/map_save.html')
    koord = session.query(Check_Map).all()
    return render_template('map.html', koord=koord)

@app.route('/destroy', methods=['GET', 'POST'])
def destroy():
    if request.method == 'POST':
        delete = session.query(Check_Map).filter_by(id=request.form['delete']).one()
        session.delete(delete)
        session.commit()
    destroys = session.query(Check_Map).all()
    return render_template('destroy.html', destroys=destroys)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if request.form.get('add') == 'add':
            newCar = Auto(mark=request.form['mark'], number=request.form['number'])
            session.add(newCar)
            session.commit()
        else:
            print('del')
            delCar = session.query(Auto).filter_by(id=request.form['delete']).one()
            session.delete(delCar)
            session.commit()
    cars = session.query(Auto).all()
    return render_template("search.html", cars=cars)



@app.route('/stream/<dir>/<width>/<height>', methods=['GET', 'POST'])
def stream(dir, width, height):
    return Response(gen(VideoCamera(), dir=dir, width=width, height=height), mimetype='multipart/x-mixed-replace; boundary=frame')




def gen(camera, dir, width, height):
    camera.camera = cv2.VideoCapture(dir)
    while True:
        frame, text, time, img = camera.get_frame(width, height)
        if len(text) != 0:
            for i in range(len(text)):
                if session.query(Auto).filter_by(number = text[i]).first():
                    print('Машина в розыске')
                    if not session.query(Check_Map).filter_by(number = text[i]).first():
                        camera_koord = session.query(Camera).filter_by(name=dir).first()
                        mark_auto = session.query(Auto).filter_by(number = text[i]).first()

                        path = 'static/img_auto/' + str(text[i]) + '_' + str(time) + '.jpg'
                        print(path)
                        cv2.imwrite(path, img)

                        add_koord = Check_Map(mark = mark_auto.mark, number = text[i], koord = camera_koord.koord, time = time, path=path)
                        session.add(add_koord)
                        session.commit()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




if __name__ == "__main__":
    app.run(debug=True)
