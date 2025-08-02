import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    error_msg = ""
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            # Optionally, check if city already exists
            existing_city = City.query.filter_by(name=new_city).first()
            if not existing_city:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_msg = "City already exists in the database."

    cities = City.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=your_api_key'

    weather_data = []

    for city in cities:
        r = requests.get(url.format(city.name)).json()
      

        if r.get('cod') == 200:
            weather = {
                'city' : city.name,
                'temperature' : r['main']['temp'],
                'description' : r['weather'][0]['description'],
                'icon' : r['weather'][0]['icon'],
            }
            weather_data.append(weather)
        else:
            # Optionally: Remove city from DB or show an error
            error_msg = f"City '{city.name}' not found!"

    return render_template('weather.html', weather_data=weather_data, error=error_msg)