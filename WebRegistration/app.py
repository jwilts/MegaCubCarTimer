from flask import Flask, render_template, request, redirect, url_for, flash
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from sqlalchemy import text
from flask_wtf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename  # Import secure_filename for file upload handling
import os
import pandas as pd
from io import BytesIO


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create the Flask application
# configure static image folder
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/jeff/cubcar_webapp/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size is 16MB


# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cubcaradmin:cubsrock@localhost/cubcar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'G8L72RR3!'  # Ensure you have a strong secret key

# Initialize the database
db = SQLAlchemy(app)

# Initialize CSRF protection after the app is defined
csrf = CSRFProtect(app)

# TrackHeatForm class for handling heat changes
class TrackHeatForm(FlaskForm):
    heat = IntegerField('Heat', validators=[DataRequired()])
    submit = SubmitField('Update')

# Models
class BacklogNotes(db.Model):
    __tablename__ = 'backlognotes'
    IssueID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BacklogEnhanceBug = db.Column(db.String(255))
    BacklogDescription = db.Column(db.String(1000))
    BacklogDetails = db.Column(db.String(1000))
    BacklogResolved = db.Column(db.Boolean)
    BacklogResolvedDate = db.Column(db.DateTime)

class RacerInfo(db.Model):
    __tablename__ = 'racerinfo'
    RacerID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RacerFirstName = db.Column(db.String(50))
    RacerLastName = db.Column(db.String(50))
    RacerPack = db.Column(db.Integer)
    RacerRFID = db.Column(db.String(60))
    RacerCarName = db.Column(db.String(255))
    RacerCarNumber = db.Column(db.Integer)
    RacerInclude = db.Column(db.Integer)
    RacerCarChecked = db.Column(db.Integer)
    RacerPitCrewName = db.Column(db.Integer)
    RacerCarWeight = db.Column(db.Numeric(10, 2))
    RacerCarClass = db.Column(db.Integer)
    RacerPhoto = db.Column(db.String(255))

class TrackInformation(db.Model):
    __tablename__ = 'trackinformation'
    TrackID = db.Column(db.Integer, primary_key=True)
    TrackName = db.Column(db.String(100))
    TrackLanes = db.Column(db.Integer)
    TrackInclude = db.Column(db.Boolean)
    TrackDigital = db.Column(db.Boolean)
    TrackControllerIP = db.Column(db.String(25))
    Heat = db.Column(db.Integer)  # Add the Heat column to track heats

class PackNames(db.Model):
    __tablename__ = 'packnames'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PackName = db.Column(db.String(100))

class PitCrewMembers(db.Model):
    __tablename__ = 'pitcrewmembers'
    ID = db.Column(db.Integer, primary_key=True)
    PitCrewMemberName = db.Column(db.String(255))
    PitCrewMemberGroup = db.Column(db.Integer)
    PitCrewMemberActive = db.Column(db.Integer)

class RaceClasses(db.Model):
    __tablename__ = 'raceclasses'
    ClassID = db.Column(db.Integer, primary_key=True)
    ClassDescription = db.Column(db.String(255))

class RaceResults(db.Model):
    __tablename__ = 'raceresults'
    RowKey = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RacerID = db.Column(db.Integer)
    RaceCounter = db.Column(db.Integer)
    RaceCarNumber = db.Column(db.Integer)
    TrackID = db.Column(db.Integer)
    Heat = db.Column(db.Integer)
    Lane = db.Column(db.Integer)
    CarName = db.Column(db.String(255))
    Pack = db.Column(db.String(120))
    RaceTime = db.Column(db.Time)
    Placing = db.Column(db.Integer)
    Status = db.Column(db.String(10))
    RacerRFID = db.Column(db.String(50))
    RacerFirstName = db.Column(db.String(60))
    RacerLastName = db.Column(db.String(60))
    RaceDate = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class ViewForm(FlaskForm):
    view_name = SelectField('View Name', choices=[])
    submit = SubmitField('View Data')

# Define the upload form using Flask-WTF
class UploadForm(FlaskForm):
    photo = FileField('Select photo')
    submit = SubmitField('Upload Photo')

# Helper function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/upload', methods=['GET', 'POST'])
def upload_photo():
    form = UploadForm()  # Create the form object
    if request.method == 'POST' and form.validate_on_submit():  # Check if it's a POST request and the form is valid
        # Check if the form has the file part
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['photo']

        # If the user does not select a file, the browser may submit an empty part
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Validate if the file has an allowed extension and save the file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save the file
            flash('File successfully uploaded!')
            return redirect(url_for('upload_photo'))  # Redirect to the same page after success

    return render_template('upload.html', form=form)  # Pass the form object to the template

@app.route('/')
def index():
    return redirect(url_for('roster'))

@app.route('/views', methods=['GET', 'POST'])
def list_views():
    form = ViewForm()
    
    # Fetch all views in the database using session.execute with text wrapping
    views = db.session.execute(text("SHOW FULL TABLES WHERE Table_type = 'VIEW'")).fetchall()

    # Populate the choices for the SelectField in the form
    form.view_name.choices = [(view[0], view[0]) for view in views]

    selected_view = None
    results = []
    columns = []

    if request.method == 'POST' and form.validate_on_submit():
        selected_view = form.view_name.data

        # Query to get data from the selected view
        query = text(f"SELECT * FROM {selected_view}")
        results = db.session.execute(query).fetchall()

        # Fetch column names
        columns = db.session.execute(query).keys()

    return render_template('list_views.html', form=form, views=views, results=results, columns=columns, selected_view=selected_view)

@app.route('/export_view/<view_name>', methods=['GET'])
def export_view(view_name):
    # Query the data from the selected view
    query = f"SELECT * FROM {view_name}"

    # Use the session's bind (engine) directly
    engine = db.session.get_bind()

    # Fetch data into a pandas DataFrame
    df = pd.read_sql(query, engine)

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=view_name)

    output.seek(0)

    # Send the file as an attachment
    return send_file(output, download_name=f'{view_name}.xlsx', as_attachment=True)


@app.route('/manage_trackheats', methods=['GET', 'POST'])
def manage_trackheats():
    form = TrackHeatForm()  # Initialize the form

    if form.validate_on_submit():  # Check if the form is submitted and valid
        track_id = request.form.get('track_id')
        heat = form.heat.data

        trackinfo = TrackInformation.query.get(track_id)
        if trackinfo:
            trackinfo.Heat = heat
            db.session.commit()
            flash('Track heat updated successfully!', 'success')
        else:
            flash('Track heat update failed.', 'danger')

    # Fetch track information entries
    trackinfo_entries = TrackInformation.query.all()

    # Pass the form to the template
    return render_template('manage_trackheats.html', trackinfo_entries=trackinfo_entries, form=form)

@app.route('/racer', methods=['GET', 'POST'])
@app.route('/racer/<int:racer_id>', methods=['GET', 'POST'])
def manage_racer(racer_id=None):
    packs = PackNames.query.all()
    pit_crews = PitCrewMembers.query.all()  # Fetch all pit crew members

    print(pit_crews)  # Debug: display the list of members in the console

    raceclasses = RaceClasses.query.all()  # Fetch race classes for the dropdown

    # If racer_id is provided, fetch the existing racer. Otherwise, prepare for adding a new racer.
    racer = RacerInfo.query.get(racer_id) if racer_id else None

    if request.method == 'POST':
        first_name = request.form.get('RacerFirstName')
        last_name = request.form.get('RacerLastName')
        pack = request.form.get('RacerPack')
        rfid = request.form.get('RacerRFID')
        car_name = request.form.get('RacerCarName')
        car_number = request.form.get('RacerCarNumber') or None
        car_checked = request.form.get('car_checked') == 'on'  # Use 'car_checked' name from the checkbox
        include_racer =  request.form.get('include_racer') == 'on' 
        # pit_crew_name = request.form.get('pit_crew_name') or None  # Use 'pit_crew_name' field name
        pit_crew_id = request.form.get('pit_crew_name')  # Get the pit crew ID        
        car_weight = request.form.get('RacerCarWeight') or None
        car_class = request.form.get('RacerCarClass') or None

        # Handle Pit Crew Name conversion to None if not selected
        # if not pit_crew_name or pit_crew_name == 'None':
        #    pit_crew_name = None

        # Handle empty pit crew selection
        pit_crew_id = int(pit_crew_id) if pit_crew_id else None


        if not first_name or not last_name or not pack or not car_name:
            flash("First Name, Last Name, Car Name, and Pack are required", "danger")
            return render_template('manage_racer.html', packs=packs, pit_crews=pit_crews, 
                                   raceclasses=raceclasses, racer=racer)

        photo = request.files.get('RacerPhoto')

        if racer:
            # Update existing racer
            racer.RacerFirstName = first_name
            racer.RacerLastName = last_name
            racer.RacerPack = pack
            racer.RacerRFID = rfid
            racer.RacerCarName = car_name
            racer.RacerCarNumber = car_number
            racer.RacerCarChecked = car_checked
            racer.RacerInclude = include_racer
            racer.RacerPitCrewName = pit_crew_id  # Store the pit crew ID            
            # racer.RacerPitCrewName = pit_crew_name
            racer.RacerCarWeight = car_weight
            racer.RacerCarClass = car_class

            if photo and photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                racer.RacerPhoto = filename  # Update racer record with the new photo path

        else:
            # Create a new racer
            new_racer = RacerInfo(
                RacerFirstName=first_name,
                RacerLastName=last_name,
                RacerPack=pack,
                RacerRFID=rfid,
                RacerCarName=car_name,
                RacerCarNumber=car_number,
                RacerCarChecked=car_checked,
                RacerInclude=include_racer,
                # RacerPitCrewName=pit_crew_name,
                RacerPitCrewName=pit_crew_id,  # Store the pit crew ID                
                RacerCarWeight=car_weight,
                RacerCarClass=car_class
            )

            if photo and photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                new_racer.RacerPhoto = filename  # Update racer record with new photo path

            db.session.add(new_racer)

        db.session.commit()
        return redirect(url_for('roster'))

    return render_template('manage_racer.html', packs=packs, pit_crews=pit_crews, 
                       raceclasses=raceclasses, racer=racer)


@app.route('/add_pitcrew', methods=['GET', 'POST'])
def add_pitcrew():
    if request.method == 'POST':
        pitcrew_name = request.form.get('PitCrewMemberName')
        if pitcrew_name:
            new_pitcrew = PitCrewMembers(
                PitCrewMemberName=pitcrew_name, 
                PitCrewMemberGroup=1, 
                PitCrewMemberActive=1
            )
            db.session.add(new_pitcrew)
            db.session.commit()
            flash('Pit Crew Member added successfully!', 'success')
            return redirect(url_for('manage_racer'))
    return render_template('add_pitcrew.html')

@app.route('/add_pack', methods=['GET', 'POST'])
def add_pack():
    if request.method == 'POST':
        pack_name = request.form.get('PackName')
        if pack_name:
            new_pack = PackNames(PackName=pack_name)
            db.session.add(new_pack)
            db.session.commit()
            flash('Pack added successfully!', 'success')
            return redirect(url_for('manage_racer'))
    return render_template('add_pack.html')

@app.route('/list_trackheats')
def list_trackheats():
    trackheats = TrackHeat.query.all()
    return render_template('list_trackheats.html', trackheats=trackheats)

@app.route('/raceresults/<int:racer_id>')
def racer_results(racer_id):
    racer = RacerInfo.query.get_or_404(racer_id)
    pack_name = db.session.query(PackNames.PackName).filter_by(ID=racer.RacerPack).scalar()
    results = db.session.query(
        RaceResults.Heat, 
        RaceResults.TrackID, 
        TrackInformation.TrackName, 
        RaceResults.Lane, 
        RaceResults.RaceTime, 
        RaceResults.Placing
    ).join(TrackInformation, RaceResults.TrackID == TrackInformation.TrackID).filter(RaceResults.RacerID == racer_id).order_by(RaceResults.Heat, RaceResults.TrackID).all()

    grouped_results = {}
    for result in results:
        heat_track_key = f"Heat {result.Heat}, Track {result.TrackID} - {result.TrackName}"
        if heat_track_key not in grouped_results:
            grouped_results[heat_track_key] = []
        grouped_results[heat_track_key].append(result)

    return render_template('racer_results.html', racer=racer, pack_name=pack_name, grouped_results=grouped_results)

@app.route('/roster')
def roster():
    racers = db.session.query(
        RacerInfo.RacerID,
        RacerInfo.RacerFirstName,
        RacerInfo.RacerLastName,
        RacerInfo.RacerCarName,  # Explicitly fetching the CarName
        RacerInfo.RacerCarChecked,  
        RacerInfo.RacerInclude,  
        RacerInfo.RacerRFID,
        PackNames.PackName  # Fetch PackName from packnames
    ).outerjoin(PackNames, RacerInfo.RacerPack == PackNames.ID).order_by(desc(RacerInfo.RacerID)).all()

    return render_template('roster.html', racers=racers)

@app.route('/race_tracker', methods=['GET'])
def race_tracker():
    # Fetch the latest race results
    results = db.session.query(
        RaceResults.Heat, 
        RaceResults.Lane, 
        RaceResults.CarName, 
        RaceResults.Pack, 
        RaceResults.RaceTime, 
        RaceResults.Placing, 
        RaceResults.RacerFirstName, 
        RaceResults.RacerLastName
    ).order_by(RaceResults.RaceDate.desc()).all()  # Order by most recent first
    
    return render_template('race_tracker.html', results=results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)



