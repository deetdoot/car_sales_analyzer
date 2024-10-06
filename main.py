from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting
import matplotlib.pyplot as plt


app = Flask(__name__)
# flask-sqlalchemy to connect to sqlite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
#Declaring the secret key
app.config["SECRET_KEY"] = "mysecret"

db = SQLAlchemy()

'''Column Names are
Date,Salesperson,Customer Name,Car Make,Car Model,Car Year,Sale Price,Commission Rate,Commission Earned'''

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250), nullable=False)
    salesperson = db.Column(db.String(250), nullable=False)
    customer_name = db.Column(db.String(250), nullable=False)
    car_make = db.Column(db.String(250), nullable=False)
    car_model = db.Column(db.String(250), nullable=False)
    car_year = db.Column(db.Integer(), nullable=False)
    sale_price = db.Column(db.String(250), nullable=False)
    commission_rate = db.Column(db.Float(), nullable=False)
    commission_earned = db.Column(db.Float(), nullable=False)

# Declaring user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(10), nullable = False, unique = True)
    password = db.Column(db.String(250), nullable = False)


# Initializing app with extension
db.init_app(app)

# Create db with app context
with app.app_context():
    db.create_all()

# Load CSV data
csv_file_path = 'data/car-data-small.csv'
car_sales_data = pd.read_csv(csv_file_path)

with app.app_context():
    db.create_all()
    for index, row in car_sales_data.iterrows():
        new_car_sale = Sales(
            date=row['Date'],
            salesperson=row['Salesperson'],
            customer_name=row['Customer Name'],
            car_make=row['Car Make'],
            car_model=row['Car Model'],
            car_year=row['Car Year'],
            sale_price=row['Sale Price'],
            commission_rate=row['Commission Rate'],
            commission_earned=row['Commission Earned']
        )
        db.session.add(new_car_sale)
    db.session.commit()
    print("Car sales data loaded successfully.")

#Initializing loginManager
loginManager = LoginManager()
loginManager.init_app(app)

@loginManager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/first_page')
def first_page():
    return render_template("first_page.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('first_page'))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    #If the user made a post request, create a new user
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    #If the user made a get request, return the register page    
    return render_template("register.html")


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/filter_by')
def filter_by():
    if request.method == "GET":
        if request.form.get("filter_by") == "Salesperson":
            filter_options = Sales.query.with_entities(Sales.salesperson).distinct().all()
        elif request.form.get("filter_by") == "Car Make":
            filter_options = Sales.query.with_entities(Sales.car_make).distinct().all()
        
        return filter_options

@app.route('/show_sales_data', defaults={'page': 1, 'records_per_page': 20})
@app.route('/show_sales_data/page/<int:page>/records_per_page/<int:records_per_page>')
def show_sales_data(page, records_per_page):
    
    filters = {}  # Initialize filters as an empty dictionary
    query = Sales.query    
    sales_data = query.paginate(page=page, per_page=records_per_page, error_out=False)
    total_records = query.count()  # Count the filtered records
    
    return render_template('show_sales_data.html', sales=sales_data, total_records=total_records, page=page, records_per_page=records_per_page, filters=filters)

@app.route('/sales_by_salesperson', methods=['GET'])
def sales_by_salesperson():

    # Query the sales data from the database
    sales_data = Sales.query.all()

    # Convert the sales data to a pandas DataFrame
    sales_df = pd.DataFrame([(s.salesperson, s.sale_price) for s in sales_data], columns=['Salesperson', 'Sale Price'])

    # Convert the sale price to numeric
    sales_df['Sale Price'] = pd.to_numeric(sales_df['Sale Price'], errors='coerce')

    # Group the data by Salesperson and sum the total price of cars sold
    sales_by_person = sales_df.groupby('Salesperson')['Sale Price'].sum()

    # Create a plot without displaying it
    plt.figure(figsize=(10, 6))
    sales_by_person.plot(kind='bar')

    # Set the labels and title
    plt.xlabel('Salesperson')
    plt.ylabel('Total Sales Price')
    plt.title('Total Sales by Salesperson')

    # Save the plot as an image
    image_path = 'static/graph.png'
    plt.savefig(image_path)

    # Close the plot to avoid displaying it
    plt.close()

    return render_template("first_page.html")


@app.route('/sales_by_car_make', methods=['GET'])
def sales_by_car_make():
    # Query the sales data from the database
    sales_data = Sales.query.all()

    # Convert the sales data to a pandas DataFrame
    sales_df = pd.DataFrame([(s.car_make, s.sale_price) for s in sales_data], columns=['Car Make', 'Sale Price'])

    # Convert the sale price to numeric
    sales_df['Sale Price'] = pd.to_numeric(sales_df['Sale Price'], errors='coerce')

    # Group the data by Car Make and sum the total price of cars sold
    sales_by_car_make = sales_df.groupby('Car Make')['Sale Price'].sum()

    # Create a plot without displaying it
    plt.figure(figsize=(10, 6))
    sales_by_car_make.plot(kind='bar')

    # Set the labels and title
    plt.xlabel('Car Make')
    plt.ylabel('Total Sales Price')
    plt.title('Total Sales by Car Make')

    # Save the plot as an image
    image_path = 'static/graph.png'
    plt.savefig(image_path)

    # Close the plot to avoid displaying it
    plt.close()

    return render_template("first_page.html")

@app.route('/delete_sales_record/<int:id>', methods=['POST'])
def delete_sales_record(id):
    print("Deleting record with id: ", id)
    sale = Sales.query.get_or_404(id)
    db.session.delete(sale)
    db.session.commit()
    return redirect(url_for('show_sales_data'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_sales_record(id):
    sale = Sales.query.get_or_404(id)
    if request.method == 'POST':
        sale.date = request.form['date']
        sale.salesperson = request.form['salesperson']
        sale.customer_name = request.form['customer_name']
        sale.car_make = request.form['car_make']
        sale.car_model = request.form['car_model']
        sale.car_year = request.form['car_year']
        sale.sale_price = request.form['sale_price']
        sale.commission_rate = request.form['commission_rate']
        sale.commission_earned = request.form['commission_earned']
        db.session.commit()
        return redirect(url_for('show_sales_data'))
        
    return render_template('edit_sales_record.html', sale=sale)

@app.route('/add_sales_record', methods=['GET', 'POST'])
def add_sales_record():
    # Adding the sales data to the database
    if request.method == 'POST':
        new_sale = Sales(
            date=request.form['date'],
            salesperson=request.form['salesperson'],
            customer_name=request.form['customer_name'],
            car_make=request.form['car_make'],
            car_model=request.form['car_model'],
            car_year=request.form['car_year'],
            sale_price=request.form['sale_price'],
            commission_rate=request.form['commission_rate'],
            commission_earned=request.form['commission_earned']
        )
        db.session.add(new_sale)
        db.session.commit()
        return redirect(url_for('show_sales_data'))
    
    return render_template('add_sales_record.html')

if __name__ == "__main__":
    app.run(debug=True)