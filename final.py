from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors


app = Flask(__name__)

conn = pymysql.connect(host='localhost',
					   user='root',
					   password='',
					   db='proj',
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def public():
    return render_template('public_info.html')

@app.route('/round_trip')
def round_trip():
    return render_template('roundtrip.html')

@app.route('/one_way_trip')
def one_way_trip():
    return render_template('onewaytrip.html')

@app.route('/round', methods=['GET', 'POST'])
def round():    
    cursor = conn.cursor()

    dep_date = request.form['departure_date']
    dep_air = request.form['departure_airport']
    arr_air = request.form['arrival_airport']
    first_query = 'SELECT Flight_num, Airline_name, Departure_date_time, Arrival_date_time, Status \
            FROM Flight \
            WHERE Departure_airport = %s AND Arrival_airport = %s AND DATE(Departure_date_time) = %s AND DATE(Departure_date_time) >= CURRENT_TIMESTAMP'

    cursor.execute(first_query, (dep_air, arr_air, dep_date))
    data = cursor.fetchall()

    return_date = request.form['return_date']
    dep_airRE = request.form['departure_airport']
    arr_airRE = request.form['arrival_airport']

    second_query = 'SELECT Flight_num, Airline_name, Arrival_date_time, Departure_date_time, Status \
        FROM Flight\
            WHERE Departure_airport = %s AND Arrival_airport = %s AND DATE(Arrival_date_time) = %s AND DATE(Arrival_date_time) >= CURRENT_TIMESTAMP'
    cursor.execute(second_query, (arr_airRE, dep_airRE, return_date))
    data1 = cursor.fetchall()


    if (data and data1):
        return render_template('roundInfo.html', data=data, data1=data1)
    else:
        error = 'No Such Future Flight Available.'
        return render_template('roundtrip.html', error=error)


@app.route('/roundInfo', methods=['GET', 'POST'])
def roundInfo():
    cursor = conn.cursor()
    query = 'SELECT Airline_name, Flight_num, Departure_date_time, Arrival_date_time, Status FROM Flight WHERE departure_date_time > CURRENT_TIMESTAMP'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close
    return render_template('onewayInfo.html', data=data)


@app.route('/oneway', methods=['GET', 'POST'])
def oneway():
    cursor = conn.cursor()
    dep_date = request.form['departure_date']
    dep_air = request.form['departure_airport']
    arr_air = request.form['arrival_airport']
    flight_info_query = 'SELECT distinct Flight_num, Airline_name, Departure_date_time, Arrival_date_time, Status \
            FROM Flight \
            WHERE Departure_airport = %s AND Arrival_airport = %s AND DATE(Departure_date_time) = %s AND DATE(Departure_date_time) >= CURRENT_TIMESTAMP'

    cursor.execute(flight_info_query, (dep_air,
                                       arr_air, dep_date))
    data = cursor.fetchall()
    cursor.close()

    if(data):
        return render_template('onewayInfo.html', data=data)
    else:
        error = 'No Such Future Flight Available.'
        return render_template('onewaytrip.html', error=error)


# @ app.route('/onewayInfo', methods=['GET', 'POST'])
# def onewayInfo():
#     cursor = conn.cursor()
#     query = 'SELECT Airline_name, Flight_num, Departure_date_time, Arrival_date_time, Status FROM Flight WHERE departure_date_time > CURRENT_TIMESTAMP'
#     cursor.execute(query)
#     data = cursor.fetchall()
#     cursor.close
#     return render_template('onewayInfo.html', data=data)


@ app.route('/combined_login')
def combined_login():
    return render_template("login_main.html")

@ app.route('/combined_register')
def combined_register():
    return render_template("register_main.html")

@ app.route('/login_main', methods=['POST', 'GET'])
def login_main():
    user = request.form['typeofuser']
    if user == "Customer":
        return redirect(url_for('login_cus'))
    elif user == "Staff":
        return redirect(url_for('login'))


@ app.route('/register_main', methods=['POST', 'GET'])
def register_main():
    user = request.form['typeofuser']
    if user == "Customer":
        return redirect(url_for('register_cus'))
    elif user == "Staff":
        return redirect(url_for('register'))



######################### CUSTOMER SIDE #######################################


@app.route('/login_cus')
def login_cus():   # login page
    return render_template('login_cus.html')

@app.route('/register_cus')
def register_cus():   # register page
    return render_template('register_cus.html')
    
@app.route('/loginAuth_cus', methods=['GET', 'POST'])
def loginAuth_cus():
    email = request.form['email']    # request from server the form-data for email
    password = request.form['password']    # request from server the form-data for password

    cursor = conn.cursor()   # cursor object which interacts with database
    query = 'SELECT Email, Password FROM Customer WHERE Email = %s AND Password = md5(%s)'   # query to get info from database
    cursor.execute(query, (email, password))  # cursor object executes the query
    data = cursor.fetchone()   # fetchone() returns an array of fetched data from executing the query  //  fetchall() if expecting multiple rows of data
    cursor.close()   # finish using the cursor object
    error = None   
    if (data):   # check if the requested form-data is contained in the database already -> valid login. if not -> throw error
        session['email'] = email   # temporary data to be stored during the time the user is logged in
        return redirect(url_for('home_cus'))
    else:
        error = 'Invalid login or username'
        return render_template('login_cus.html', error=error)

@app.route('/registerAuth_cus', methods=['GET', 'POST'])
def registerAuth_cus(): # need to change registration input forms
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_num = request.form['building_num']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_num = request.form['phone_num']
    passport_num = request.form['passport_num']
    passport_expire = request.form['passport_expire']
    passport_country = request.form['passport_country']
    dob = request.form['dob']
    cursor = conn.cursor()
    query = 'SELECT * FROM Customer WHERE Email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()
    error = None
    if(data):
        error = "This customer already exists"
        return render_template('register_cus.html', error=error)
    else:
        insertQuery = 'INSERT INTO Customer VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(insertQuery, (email, name, password, building_num, street, city, state, phone_num, passport_num, passport_expire, passport_country, dob))
        conn.commit()  # basically allows Python to modify tables in the SQL database
        cursor.close()
        return render_template('public_info.html')

@app.route('/home_cus')
def home_cus():    # home page where all customer-use cases will be available


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT Name FROM Customer WHERE Email = %s'
    cursor.execute(query, (email))
    name = cursor.fetchone()['Name']
    cursor.close()
    return render_template('home_cus.html',name=name)

@app.route('/view_cus')
def view_flight_cus():    # task no. 4

    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT Flight_num, Departure_date_time, Airline_name, Departure_airport, Arrival_airport, Status FROM Ticket NATURAL JOIN Flight WHERE Email = %s AND departure_date_time > CURRENT_TIMESTAMP'
    cursor.execute(query, email)
    data = cursor.fetchall()
    cursor.close()
    return render_template('flights_cus.html', email=email, data=data)

@app.route('/search_cus')
def search_cus():


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    return render_template('search_cus.html')

@app.route('/search_flight_cus', methods=['GET', 'POST'])
# search based on departure airport, arrival airport, departure time
def search_flight_cus(): # task no. 5


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    cursor = conn.cursor()
    dep_date = request.form['departure_date']
    dep_port = request.form['departure_airport']
    arr_port = request.form['arrival_airport']
    query = 'SELECT distinct Flight_num, Airline_name, Departure_date_time \
            FROM Flight \
            WHERE Departure_airport = %s AND Arrival_airport = %s AND DATE(Departure_date_time) = %s AND DATE(Departure_date_time) >= CURRENT_TIMESTAMP'
    cursor.execute(query, (dep_port, arr_port, dep_date))
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        session['search_data'] = data
        return render_template('result_cus.html', data=data)
    else:
        error='No Such Future Flight Available.'
        return render_template('search_cus.html',error=error)

@app.route('/result_cus', methods = ['GET','POST'])
def search_result_cus():


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    session['flight_num'] = request.form['Flight_num']
    session['airline_name'] = request.form['Airline_name']
    session['departure_date_time'] = request.form['Departure_date_time']
    #date_idx = session['departure_date_time'].find(' ')
    #departure_date_only = session['departure_date_time'][:date_idx]
    cursor = conn.cursor()
    # Retrieve base price of flight
    query0 = 'SELECT Price FROM Flight WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s'
    cursor.execute(query0, (session['flight_num'], session['departure_date_time'], session['airline_name']))
    data0 = cursor.fetchone()
    error=None
    if not data0:
        error='No Such Flight Exists'
        return render_template('result_cus.html',error=error, data=session['search_data'])
    base_price = data0['Price']
    # Retrieve seat capacity of the plane
    query1 = 'SELECT Num_seats FROM Flight natural join Airplane WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s'
    cursor.execute(query1, (session['flight_num'], session['departure_date_time'], session['airline_name']))
    seat_cap = cursor.fetchone()['Num_seats']
    # Retrieve the number of tickets bought for chosen flight
    query2 = 'SELECT count(Ticket_ID) as Booked_seats FROM Ticket natural join Flight WHERE Flight_num = %s AND Airline_name = %s AND Departure_date_time = %s'
    cursor.execute(query2, (session['flight_num'], session['airline_name'], session['departure_date_time']))
    seats_taken = cursor.fetchone()['Booked_seats']
    if seats_taken/seat_cap >= 0.75:
        session['sold_price'] = float(base_price)*1.25
    else:
        session['sold_price'] = base_price
    cursor.close()
    return render_template('ticket_cus.html', data=session['sold_price'])

@app.route('/ticket_cus')
def ticket_cus():

    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    return render_template('ticket_cus.html')

@app.route('/purchase_cus', methods = ['GET','POST'])
def purchase_ticket_cus():    # task no. 6


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    flight_num = session['flight_num']
    airline_name = session['airline_name']
    departure_date_time = session['departure_date_time']
    #date_idx = session['departure_date_time'].find(' ')
    #departure_date_only = session['departure_date_time'][:date_idx]
    sold_price = session['sold_price']
    cursor = conn.cursor()
    # check if ticket has already been purchased
    query0 = 'SELECT * FROM Ticket WHERE Email = %s AND Flight_num = %s AND Airline_name = %s AND Departure_date_time = %s'
    cursor.execute(query0, (email, flight_num, airline_name, departure_date_time))
    data0 = cursor.fetchall()
    error = None
    if data0:
        error='Already purchased this ticket'
        return render_template('result_cus.html', error=error, data=session['search_data'])
    # check if there are any seats left in the plane
    query01 = 'SELECT count(Ticket_ID) as Booked_seats FROM Ticket natural join Flight WHERE Flight_num = %s AND Airline_name = %s AND Departure_date_time = %s'
    cursor.execute(query01, (flight_num, airline_name, departure_date_time))
    seats_taken = cursor.fetchone()['Booked_seats']
    query02 = 'SELECT Num_seats FROM Flight natural join Airplane WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s'
    cursor.execute(query02, (flight_num, departure_date_time, airline_name))
    seat_cap = cursor.fetchone()['Num_seats']
    if seats_taken >= seat_cap:
        error='Plane is full'
        return render_template("ticket_cus.html", error=error)
    # if ticket has not yet been purchased and there is at least one seat available
    card_type = request.form['card_type']
    card_number = request.form['card_number']
    name_on_card = request.form['name_on_card']
    card_exp_date = request.form['card_exp_date']
    ticket_id = randint(100000,999999)
    query1 = 'SELECT * FROM Ticket WHERE Ticket_ID = %s'
    cursor.execute(query1, (ticket_id))
    data1 = cursor.fetchall()
    while data1:
        ticket_id = randint(100000,999999)
        cursor.execute(query1, (ticket_id))
    query2 = 'INSERT INTO Ticket VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)'
    cursor.execute(query2, (ticket_id,email,sold_price,card_type,card_number,name_on_card,card_exp_date,airline_name,flight_num,departure_date_time))
    conn.commit()
    cursor.close()
    session.pop('flight_num')
    session.pop('airline_name')
    session.pop('departure_date_time')
    session.pop('sold_price')
    session.pop('search_data')
    #return redirect('/search')
    return render_template("search_cus.html", msg='Purchase Successful');

@app.route('/past_cus')
def past_flights_cus():   # page to view past flights


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    cursor = conn.cursor()


    # load past flights from Flight table
    past_flight_q = "SELECT Flight.Flight_num, Flight.Departure_date_time, Flight.Airline_name\
                     FROM Flight, Ticket\
                     WHERE Flight.Flight_num = Ticket.Flight_num AND\
                           Flight.Departure_date_time = Ticket.Departure_date_time AND\
                           Flight.Airline_name = Ticket.Airline_name AND\
                           Flight.Arrival_date_time <= CURRENT_TIMESTAMP AND\
                           Ticket.Email = %s"

    cursor.execute(past_flight_q, (email))
    past_data = cursor.fetchall()


    # load past comments and ratings from Fly
    rating_comment_query = 'SELECT Flight_num, Departure_date_time, Airline_name, Rating, Comment \
                            FROM Fly \
                            WHERE Email = %s AND \
                                  Departure_date_time <= CURRENT_TIMESTAMP'

    cursor.execute(rating_comment_query, (email))
    rating_comment_data = cursor.fetchall()

    cursor.close()
    error = None

    print(past_data)

    if past_data:
        return render_template('past_cus.html', data=past_data, comment_data=rating_comment_data)
    else:
        error='You have no previous flights'
        return render_template('home_cus.html', error=error)
    

@app.route('/post_cus', methods = ['GET','POST'])
def post_cus():    # task no. 7


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    flight_num = request.form['flight_num']
    airline_name = request.form['airline_name']
    departure_date_time = request.form['departure_date_time'] # YYYY-MM-DDThh:mm
    comment = request.form['comment']
    rating = request.form['rating']
    cursor = conn.cursor()
    # check if customer is trying to post on a flight he/she didn't take
    query0 = 'SELECT * \
              FROM Flight, Ticket \
              WHERE Ticket.Email = %s AND \
                    Ticket.Flight_num = %s AND \
                    Ticket.Airline_name = %s AND \
                    Ticket.Departure_date_time = %s AND\
                    Ticket.Departure_date_time = Flight.Departure_date_time AND \
                    Ticket.Airline_name = Flight.Airline_name AND \
                    Ticket.Flight_num = Flight.Flight_num AND \
                    Ticket.Departure_date_time <= CURRENT_TIMESTAMP'

    cursor.execute(query0, (email,flight_num,airline_name,departure_date_time))
    data0 = cursor.fetchall()
    error=None

    if data0:
        # Each new comment/rating replaces the old one
        # First check if the customer already commented or rated before. 

        check_query = 'SELECT * FROM Fly WHERE Email = %s AND Flight_num = %s AND Airline_name = %s AND Departure_date_time = %s'
        cursor.execute(check_query, (email, flight_num, airline_name, departure_date_time))
        check_data = cursor.fetchall()

        if check_data: # if there is already data from the user, delete it first. 
            query1 = 'DELETE FROM Fly WHERE Email = %s AND Flight_num = %s AND Airline_name = %s AND Departure_date_time = %s'
            cursor.execute(query1, (email,flight_num,airline_name,departure_date_time))


        query2 = 'INSERT INTO Fly VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query2, (email, flight_num, departure_date_time, airline_name, rating, comment))
        conn.commit()
        cursor.close()
        return redirect(url_for('past_flights_cus'))
    else:
        error='You cannot commment/rate on a flight you did not take'
        cursor.close()
        return render_template('home_cus.html', error=error)

@app.route('/track_cus')
def track_spendings_cus():


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    cursor = conn.cursor()
    # get current date and set the range for a full year before
    query0 = 'SELECT current_date'
    cursor.execute(query0)
    end_date = cursor.fetchone()['current_date']   # current date
    # get date 1 year before current date
    query1 = 'select DATE_ADD(current_date, interval -1 year) as prior_year_date'
    cursor.execute(query1)
    start_date_total = cursor.fetchone()['prior_year_date']
    # get date 6 months before current date
    query2 = 'select DATE_ADD(current_date, interval -6 month) as prior_6mon_date'
    cursor.execute(query2)
    start_date_range = cursor.fetchone()['prior_6mon_date']
    # get total spendings from start_date_total to end_date (current date)
    query3 = 'SELECT SUM(Sold_price) as Total_Spending FROM Ticket WHERE Email = %s AND %s <= DATE(Purchase_date_time) AND DATE(Purchase_date_time) <= %s'
    cursor.execute(query3, (email, start_date_total, end_date))
    total_spending = cursor.fetchone()['Total_Spending']
    # get each individual ticket price paid and the month of purchase
    query4 = 'SELECT SUM(Sold_price) as Total_Spending, MONTH(DATE(Purchase_date_time)) as Month FROM Ticket WHERE Email = %s AND %s <= DATE(Purchase_date_time) AND DATE(Purchase_date_time) <= %s GROUP BY Month'
    cursor.execute(query4, (email, start_date_range, end_date))
    data = cursor.fetchall()
    cursor.close()
    return render_template('track_cus.html', start_date=start_date_total, start_date_range=start_date_range, end_date=end_date, total_spending=total_spending,data=data)

@app.route('/display_cus', methods=['GET','POST'])
def display_spendings_cus():


    if "email" not in session:
        error = "You need to be logged in as a customer to visit this page"
        return render_template('login_cus.html', error=error)


    email = session['email']
    cursor = conn.cursor()
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    # get total spending from start to end date
    query0 = 'SELECT SUM(Sold_price) as Total_Spending FROM Ticket WHERE Email = %s AND %s <= DATE(Purchase_date_time) AND DATE(Purchase_date_time) <= %s'
    cursor.execute(query0, (email, start_date, end_date))
    total_spending = cursor.fetchone()['Total_Spending']
    # get each individual ticket price paid and the month of purchase
    query1 = 'SELECT SUM(Sold_price) as Total_Spending, MONTH(DATE(Purchase_date_time)) as Month FROM Ticket WHERE Email = %s AND %s <= DATE(Purchase_date_time) AND DATE(Purchase_date_time) <= %s GROUP BY Month'
    cursor.execute(query1, (email, start_date, end_date))
    data = cursor.fetchall()
    '''
    error = None
    if total_spending:
        if data:
            return render_template('track.html', start_date=start_date, start_date_range=start_date, end_date=end_date, total_spending=total_spending, data=data)
    error = 'Invalid date input(s)'
    return render_template('track.html', start_date=start_date, start_date_range=start_date, end_date=end_date, error=error)
    '''
    return render_template('track_cus.html', start_date=start_date, start_date_range=start_date, end_date=end_date, total_spending=total_spending, data=data)


@app.route('/logout_cus')
def logout_cus():  # logout action  --  task no. 9
    if 'flight_num' in session:
        session.pop('flight_num')
    if 'airline_name' in session:
        session.pop('airline_name')
    if 'departure_date_time' in session:
        session.pop('departure_date_time')
    if 'search_data' in session:
        session.pop('search_data')

    session.pop('email')

    return redirect('/')


################################################################################




@app.route('/Customer_log')
def hi():
	return render_template('front_cus.html')

@app.route('/Staff_log')
def hola():
	return render_template('index.html')

@app.route('/login')
def login():
	return render_template('staff_login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('staff_register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Staff WHERE Username = %s and Password = md5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('staffhome'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('staff_login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']    
    date_of_birth = request.form['date_of_birth']
    airline_name = request.form['airline_name']
    numbers = request.form['phone_num']

    numbers = numbers.split(";")
    print(numbers)

    # print(username, password, first_name, last_name, date_of_birth, airline_name)

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    user_query = 'SELECT * FROM Staff WHERE username = %s'
    cursor.execute(user_query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This staff already exists"
        return render_template('staff_register.html', error = error)
    else:

        airline_query = 'SELECT * FROM Airline WHERE Name = %s'
        cursor.execute(airline_query, (airline_name))
        data = cursor.fetchone()
        error = None
        if (not data):
            error = "This airline does not exist"
            return render_template('staff_register.html', error=error)
        else:
            ins = 'INSERT INTO Staff VALUES(%s, md5(%s), %s, %s, %s, %s)'
            cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
            insert_number_q = "INSERT INTO Phone_num VALUES (%s, %s)"
            
            for num in numbers:
                stripped = num.strip()

                if len(stripped) == 10:
                    cursor.execute(insert_number_q, (username, stripped))
                else:
                    error = "Please enter valid phone number"
                    return render_template('staff_register.html', error=error)
                
            conn.commit()
            cursor.close()
            return render_template('public_info.html')

@app.route('/logout')
def logout():
	session.pop('username')
	if session.get('most_freq_name'):
		session.pop('most_freq_name')
	if session.get('past_month_sales'):
		session.pop('past_month_sales')
	if session.get('past_year_sales'):
		session.pop('past_year_sales')
	return redirect('/')


@app.route('/staffhome')
def staffhome():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name, First_name, Last_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']
	f_name = data['First_name']
	l_name = data['Last_name']

	cursor.close()

	return render_template('airline_staff_home.html', airline = airline, f_name = f_name, l_name = l_name)
	

@app.route('/viewFlights')
def viewFlights():


	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']

	cursor = conn.cursor()
	
	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']


	#default 30 days in the future
	flight_info_query = 'SELECT Flight_num, Departure_date_time, Arrival_date_time, Departure_airport, Arrival_airport\
    				     FROM Flight\
    				     WHERE (Departure_date_time BETWEEN DATE(CURRENT_TIMESTAMP) AND Date_ADD(DATE(CURRENT_TIMESTAMP), INTERVAL 30 DAY)) and Airline_name = %s '

	#print(flight_info_query, (airline))

	cursor.execute(flight_info_query, (airline))
	data = cursor.fetchall()
	#print("All the data:", data)

	cursor.execute("SELECT DATE(CURRENT_TIMESTAMP) as time, Date_ADD(DATE(CURRENT_TIMESTAMP), INTERVAL 30 DAY) as future_time")
	curr_date = cursor.fetchone()
	s_date = curr_date["time"]
	e_date = curr_date["future_time"]

	cursor.close()

	return render_template('viewFlights.html', posts=data, airline=airline, start = s_date, end = e_date, customers = None, both=None, dst=None, arr=None)

#source/destination airports/city etc

@app.route('/post_date', methods=['GET', 'POST'])
def post_date():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	start_date = request.form["start_time"]
	end_date = request.form["end_time"]

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	flight_info_query = 'SELECT Flight_num, Departure_date_time, Arrival_date_time, Departure_airport, Arrival_airport\
    				     FROM Flight\
    				     WHERE (Departure_date_time BETWEEN %s AND %s) \
    				     	   and Airline_name = %s'

	cursor.execute(flight_info_query, (start_date, end_date, airline))
	data = cursor.fetchall()
	print(data)

	cursor.close()

	return render_template('viewFlights.html', posts = data, airline=airline, start=start_date, end=end_date, customers = None, both=None, dst=None, arr=None)

@app.route('/post_airport', methods=['GET', 'POST'])
def post_airport():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	dst_airport = request.form["dst_airport"]
	arr_airport = request.form["arr_airport"]

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	flight_info_query = 'SELECT Flight_num, Departure_date_time, Arrival_date_time, Departure_airport, Arrival_airport\
    				     FROM Flight\
    				     WHERE Departure_airport = %s\
    				     		AND Arrival_airport = %s AND Airline_name = %s'

	cursor.execute(flight_info_query, (dst_airport, arr_airport, airline))
	data = cursor.fetchall()

	cursor.close()

	return render_template('viewFlights.html', posts = data, airline=airline, start=dst_airport, end=arr_airport, customers = None, both=None, dst=None, arr=None)

@app.route('/post_city', methods=['GET', 'POST'])
def post_city():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	dst_city = request.form["dst_city"]
	arr_city = request.form["arr_city"]

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	subquery_dst = ""
	subquery_arr = ""

	flight_info_query = 'SELECT dst.Flight_num, dst.Departure_date_time, dst.Arrival_date_time, dst.Departure_airport, dst.Arrival_airport\
    				     FROM (SELECT Flight.Flight_num, Flight.Departure_date_time, Flight.Arrival_date_time, Flight.Departure_airport, Flight.Arrival_airport, Flight.Airline_name\
								FROM Flight, Airport\
								WHERE Flight.Departure_airport = Airport.Code AND\
						  		Airport.City = %s) as dst, \
						  		(SELECT Flight.Flight_num, Flight.Departure_date_time, Flight.Arrival_date_time, Flight.Departure_airport, Flight.Arrival_airport, Flight.Airline_name\
								FROM Flight, Airport\
								WHERE Flight.Arrival_airport = Airport.Code AND\
						  				Airport.City = %s) as arr\
    				     WHERE dst.Flight_num = arr.Flight_num AND\
    				     	   dst.Departure_date_time = arr.Departure_date_time AND\
    				     	   dst.Airline_name = arr.Airline_name AND\
    				     	   dst.Airline_name = %s'

	cursor.execute(flight_info_query, (dst_city, arr_city, airline))
	data = cursor.fetchall()

	cursor.close()

	return render_template('viewFlights.html', posts = data, airline=airline, start=dst_city, end=arr_city, customers = None, both=None, dst=None, arr=None)


@app.route('/post', methods=['GET', 'POST'])
def post():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	start_date = request.form["start_time"]
	end_date = request.form["end_time"]
	dst_airport = request.form["dst_airport"]
	arr_airport = request.form["arr_airport"]

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	flight_info_query = 'SELECT Flight_num, Departure_date_time, Arrival_date_time, Departure_airport, Arrival_airport\
    				     FROM Flight\
    				     WHERE (Departure_date_time BETWEEN %s AND %s) \
    				     	   and Airline_name = %s\
    				     	   and Departure_airport = %s\
    				     	   and Arrival_airport = %s'

	cursor.execute(flight_info_query, (start_date, end_date, airline, dst_airport, arr_airport))
	data = cursor.fetchall()

	cursor.close()

	return render_template('viewFlights.html', posts = data, airline=airline, start=start_date, end=end_date, customers = None, both=True, dst=dst_airport, arr=arr_airport)


@app.route('/viewCustomers', methods=['GET', 'POST'])
def viewCustomers():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	Flight_num = request.form["Flight_num"]
	dep_date_time = request.form["Departure_date_time"]

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	#check flight info.
	check_flight_q = 'SELECT * FROM Flight WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s'
	cursor.execute(check_flight_q, (Flight_num, dep_date_time, airline))
	flight_data = cursor.fetchone()

	if not flight_data:
		error = "There is no flight with the provided information. Go back and enter again."
		return render_template('view_customers.html', posts = None, airline=airline, Flight_num=Flight_num, error=error)

		

	customer_q = 'SELECT distinct Email, Name\
    				     FROM Ticket NATURAL JOIN Customer\
    				     WHERE Departure_date_time = %s\
    				     	   and Airline_name = %s\
    				     	   and Flight_num = %s'

	cursor.execute(customer_q, (dep_date_time, airline, Flight_num))
	data = cursor.fetchall()

	cursor.close()

	if not data:
		error = "No customers for this flight!"
		return render_template('view_customers.html', posts = None, airline=airline, Flight_num=Flight_num, error=error)


	return render_template('view_customers.html', posts = data, airline=airline, Flight_num=Flight_num)



@app.route('/new_flight')
def new_flight():
	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	return render_template('new_flight.html', error=None)

@app.route('/new_flight_form', methods=['GET', 'POST'])
def new_flight_form():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']

	cursor = conn.cursor();

	#check the types of request.form[x]. If int/float, convert to str

	Flight_num = request.form['Flight_num']
	Dep_date_time = request.form['Departure_date_time']
	Arr_date_time = request.form['Arrival_date_time']
	Plane_ID = request.form['Plane_ID']
	Price = request.form['Price']
	Dep_airport = request.form['Departure_airport']
	Arr_airport = request.form['Arrival_airport']
	Status = request.form['Status']

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	Airline_name = data['Airline_name']

	#checks
	flight_num_q = "SELECT Flight_num FROM Flight WHERE Flight_num = %s AND Airline_name = %s"
	cursor.execute(flight_num_q, (Flight_num, Airline_name))
	data = cursor.fetchone()
	if data:
		return render_template('new_flight.html', error="Already have this flight number")

	plane_ID_q = "SELECT Plane_ID FROM Airplane WHERE Plane_ID = %s AND Airline_name = %s"
	cursor.execute(plane_ID_q, (Plane_ID, Airline_name))
	data = cursor.fetchone()
	if not data:
		return render_template('new_flight.html', error="No matching airplane ID")

	dep_airport_q = "SELECT Code FROM Airport WHERE Code = %s"
	cursor.execute(dep_airport_q, (Dep_airport))
	data = cursor.fetchone()
	if not data:
		return render_template('new_flight.html', error="Not a valid departure airport")

	arr_airport_q = "SELECT Code FROM Airport WHERE Code = %s"
	cursor.execute(arr_airport_q, (Arr_airport))
	data = cursor.fetchone()
	if not data:
		return render_template('new_flight.html', error="Not a valid arrival airport")

	query = 'INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(query, (Flight_num, Dep_date_time, Airline_name, Plane_ID, Arr_date_time, Price, Dep_airport, Arr_airport, Status))
	conn.commit()
	cursor.close()

	return redirect(url_for('showFuture'))

@app.route('/showFuture')
def showFuture():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session["username"]
	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	airline = data['Airline_name']

	flight_info_query = 'SELECT Flight_num, Departure_date_time\
    				     FROM Flight\
    				     WHERE (Departure_date_time BETWEEN DATE(CURRENT_TIMESTAMP) AND Date_ADD(DATE(CURRENT_TIMESTAMP), INTERVAL 30 DAY)) and Airline_name = %s '

	print(flight_info_query, (airline))

	cursor.execute(flight_info_query, (airline))
	data = cursor.fetchall()

	cursor.execute("SELECT DATE(CURRENT_TIMESTAMP) as time, Date_ADD(DATE(CURRENT_TIMESTAMP), INTERVAL 30 DAY) as future_time")
	curr_date = cursor.fetchone()
	s_date = curr_date["time"]
	e_date = curr_date["future_time"]

	cursor.close()

	return render_template('success_add_flight.html', data=data, s_date=s_date, e_date=e_date, airline=airline)


@app.route('/change_status')
def change_status():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	return render_template('change_status.html', error=None)

@app.route('/change_flight_status', methods=['GET','POST'])
def change_flight_status():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor();

	Flight_num = request.form['Flight_num']
	Dep_date_time = request.form['Departure_date_time']

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s'
	cursor.execute(airline_query, (username))
	data = cursor.fetchone()
	Airline_name = data['Airline_name']

	#checks
	flight_q = "SELECT Status FROM Flight WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s"
	print(Flight_num, Airline_name, Dep_date_time)
	cursor.execute(flight_q, (Flight_num, Dep_date_time, Airline_name))
	data = cursor.fetchone()
	if not data:
		return render_template("change_status.html", error="No matching flight with the given information. Check again.")

	status = data["Status"]

	new_status = "On-time"

	#check the return type of fetchone and fetchall()
	if status == "On-time":
		new_status = "Delayed"

	store_query = "SELECT Flight_num, Departure_date_time, Airline_name, Plane_ID, Arrival_date_time, Price, Departure_airport, Arrival_airport\
				   FROM Flight\
				   WHERE Flight_num = %s AND\
				         Airline_name = %s AND\
				         Departure_date_time = %s;"

	cursor.execute(store_query, (Flight_num, Airline_name, Dep_date_time))
	store_data = cursor.fetchone()

	delete_query = "DELETE FROM Flight WHERE Flight_num = %s AND\
				         Airline_name = %s AND\
				         Departure_date_time = %s;"
	cursor.execute(delete_query, (Flight_num, Airline_name, Dep_date_time))

	insert_query = "INSERT INTO Flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	Plane_ID = store_data["Plane_ID"]
	Arr_date_time = store_data["Arrival_date_time"]
	Price = store_data["Price"]
	dep_airport = store_data["Departure_airport"]
	arr_airport = store_data["Arrival_airport"]

	cursor.execute(insert_query, (Flight_num, Dep_date_time, Airline_name, Plane_ID, Arr_date_time, Price, dep_airport, arr_airport, new_status))

	conn.commit()
	cursor.close()

	return redirect(url_for('staffhome'))

@app.route('/confirm_insert_plane', methods=["GET", "POST"])
def confirm_insert_plane():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']
	Plane_ID = session['Plane_ID']
	Num_seats = session['Num_seats']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()['Airline_name']

	insert_query = 'INSERT INTO Airplane VALUES(%s, %s, %s)'
	cursor.execute(insert_query, (Plane_ID, airline_name, Num_seats))
	conn.commit()

	#delete from cookie because we no longer need it
	session.pop("Plane_ID")
	session.pop("Num_seats")

	cursor.close()

	return redirect(url_for('staffhome'))

@app.route('/confirmation_plane')
def confirmation_plane():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']
	cursor = conn.cursor()

	Plane_ID = session["Plane_ID"]
	Num_seats = session["Num_seats"]

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()['Airline_name']

	query = 'SELECT Plane_ID, Num_seats\
			 FROM Airplane\
			 WHERE Airline_name = %s'

	cursor.execute(query, (airline))
	data = cursor.fetchall()
	cursor.close()

	return render_template('plane_confirmation.html', airline = airline, data=data, Plane_ID=Plane_ID, Num_seats=Num_seats)


@app.route('/add_airplane')
def add_airplane():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']
	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]
	cursor.close()

	return render_template('add_airplane.html', error=None, airline=airline_name)

@app.route('/insert_airplane', methods=['GET', 'POST'])
def insert_airplane():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	Plane_ID = request.form['Plane_ID']
	Num_seats = request.form['Num_seats']

	#check for duplicates
	plane_q = "SELECT Plane_ID FROM Airplane WHERE Plane_ID = %s AND Airline_name = %s"
	cursor.execute(plane_q, (Plane_ID, airline_name))
	data = cursor.fetchone()
	if data:
		return render_template('add_airplane.html', error="Already existing Plane ID!", airline=airline_name)

	#store on the cookie
	session["Plane_ID"] = Plane_ID
	session["Num_seats"] = Num_seats
	
	
	cursor.close()

	return redirect(url_for('confirmation_plane'))


@app.route('/add_airport')
def add_airport():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	return render_template('add_airport.html', error=None)


@app.route('/insert_airport', methods=['GET', 'POST'])
def insert_airport():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor()

	Code = request.form['Code']
	Name = request.form['Name']
	City = request.form['City']

	code_q = "SELECT * FROM Airport WHERE Code = %s"
	cursor.execute(code_q, (Code))
	data = cursor.fetchone()

	if data:
		return render_template('add_airport.html', error="Already existing airport Code!")

	insert_q = "INSERT INTO Airport VALUES(%s, %s, %s)"
	cursor.execute(insert_q, (Code, Name, City))
	cursor.close()
	conn.commit()

	return redirect(url_for('staffhome'))


@app.route('/view_ratings')
def view_ratings():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	average_q = 'SELECT Flight_num, Departure_date_time, avg(Rating) as average_rating\
				FROM fly\
				WHERE Airline_name = %s\
				GROUP BY Flight_num, Departure_date_time'


	cursor.execute(average_q, (airline_name))
	data = cursor.fetchall()

	cursor.close()

	return render_template('view_ratings.html', data=data, airline=airline_name, add_data=None, error=None)

@app.route('/which_flight', methods=['GET', 'POST'])
def which_flight():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	average_q = 'SELECT Flight_num, Departure_date_time, avg(Rating) as average_rating\
				FROM fly\
				WHERE Airline_name = %s\
				GROUP BY Flight_num, Departure_date_time'


	cursor.execute(average_q, (airline_name))
	data = cursor.fetchall()

	flight_num = request.form['Flight_num']
	dep_date_time = request.form['Departure_date_time']

	check_flight_q = 'SELECT * FROM Flight WHERE Flight_num = %s AND Departure_date_time = %s AND Airline_name = %s'
	cursor.execute(check_flight_q, (flight_num, dep_date_time, airline_name))
	flight_data = cursor.fetchone()

	if not flight_data:
		error = "There is no flight with the provided information. Enter again."
		return render_template('view_ratings.html', data=data, airline=airline_name, add_data=None, error=error)

	comments_ratings_q = 'SELECT Flight_num, Departure_date_time, Rating, Comment \
				FROM fly\
				WHERE Airline_name = %s AND Flight_num = %s AND Departure_date_time = %s'

	cursor.execute(comments_ratings_q, (airline_name, flight_num, dep_date_time))
	data_add = cursor.fetchall() 
	cursor.close()

	if not data_add:
		error = "There are no ratings and comments in the given flight."
		return render_template('view_ratings.html', data=data, airline=airline_name, add_data=None, error=error)

	return render_template('view_ratings.html', data=data, airline=airline_name, add_data=data_add, error=None)


@app.route('/view_earned_revenue')
def view_earned_revenue():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	last_month_q = "SELECT SUM(Sold_price) as Last_Month_Sale\
					FROM Ticket \
					WHERE Airline_name = %s AND\
						  (Purchase_date_time BETWEEN Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -30 DAY) AND date(CURRENT_TIMESTAMP))"

	cursor.execute(last_month_q, (airline_name))
	last_month = cursor.fetchone()["Last_Month_Sale"]

	lm_start_end_q = "SELECT Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -30 DAY) as lm_start, date(CURRENT_TIMESTAMP) as lm_end"
	cursor.execute(lm_start_end_q)
	lm_start_end = cursor.fetchone()
	lm_start = lm_start_end["lm_start"]
	lm_end = lm_start_end["lm_end"]
	#print(lm_start_end)

	last_year_q = "SELECT SUM(Sold_price) as Last_Year_Sale\
					FROM Ticket \
					WHERE Airline_name = %s AND\
						  (Purchase_date_time BETWEEN Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -1 YEAR) AND date(CURRENT_TIMESTAMP))"

	cursor.execute(last_year_q, (airline_name))
	last_year = cursor.fetchone()["Last_Year_Sale"]

	ly_start_end_q = "SELECT Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -1 YEAR) as ly_start, date(CURRENT_TIMESTAMP) as ly_end"
	cursor.execute(ly_start_end_q)
	ly_start_end = cursor.fetchone()
	ly_start = ly_start_end["ly_start"]
	ly_end = ly_start_end["ly_end"]

	cursor.close()

	return render_template('view_earned_revenue.html', last_month=last_month, last_year=last_year, airline=airline_name, error=None, lm_start=lm_start, lm_end=lm_end, \
		ly_start = ly_start, ly_end=ly_end)

@app.route('/view_top_destination')
def view_top_destination():

	found_all_month = 0
	top_3_destination_month = []

	found_all_year = 0
	top_3_destination_year = []

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']

	cursor = conn.cursor()

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	#date based on the arrival date
	monthly_sub_q = "SELECT Airport.City, COUNT(Ticket.Ticket_ID) as total_sold_tickets\
					 FROM Ticket, Flight, Airport\
					 WHERE Ticket.Airline_name = Flight.Airline_name AND\
						   Ticket.Flight_num = Flight.Flight_num AND\
						   Ticket.Departure_date_time = Flight.Departure_date_time AND\
						   Flight.Arrival_airport = Airport.Code AND\
						   Flight.Airline_name = %s AND\
						   (Flight.Arrival_date_time BETWEEN Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -30 DAY) AND date(CURRENT_TIMESTAMP))\
					GROUP BY Airport.City"

	yearly_sub_q =  "SELECT Airport.City, COUNT(Ticket.Ticket_ID) as total_sold_tickets\
					 FROM Ticket, Flight, Airport\
					 WHERE Ticket.Airline_name = Flight.Airline_name AND\
						   Ticket.Flight_num = Flight.Flight_num AND\
						   Ticket.Departure_date_time = Flight.Departure_date_time AND\
						   Flight.Arrival_airport = Airport.Code AND\
						   Flight.Airline_name = %s AND\
						   (Flight.Arrival_date_time BETWEEN Date_ADD(date(CURRENT_TIMESTAMP), INTERVAL -1 YEAR) AND date(CURRENT_TIMESTAMP))\
					GROUP BY Airport.City"


	top_destination_q = "SELECT tops.City, tops.total_sold_tickets\
						FROM ({}) as tops\
						WHERE tops.total_sold_tickets in (SELECT MAX(max_tickets.total_sold_tickets)\
														  FROM ({}) as max_tickets)"

	top_destination_q_month = top_destination_q.format(monthly_sub_q, monthly_sub_q)
	top_destination_q_year = top_destination_q.format(yearly_sub_q, yearly_sub_q)

	cursor.execute(top_destination_q_month, (airline_name, airline_name))
	top_city_month = cursor.fetchall()

	# if top_city == None:
	# 	return render_template('view_top_destination.html', airline=airline_name, top_des=top_3_destination)

	cursor.execute(top_destination_q_year, (airline_name, airline_name))
	top_city_year = cursor.fetchall()


	for line in top_city_month:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_month.append(top_city_dict)


	for line in top_city_year:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_year.append(top_city_dict)

	found_all_month += len(top_city_month)
	found_all_year += len(top_city_year)


	print("1st q, month:", top_3_destination_month)
	print("1st q, year:", top_3_destination_year)


	while found_all_month > 3:
		top_3_destination_month.pop()
		found_all_month.pop()

	while found_all_year > 3:
		top_3_destination_year.pop()
		found_all_year.pop()

	if found_all_year == 3 and found_all_month == 3:
		return render_template('view_top_destination.html', airline=airline_name, top_des_m=top_3_destination_month, top_des_y=top_3_destination_year)


	second_top_destination_q = "SELECT tops.City, tops.total_sold_tickets\
								FROM ({}) as tops\
								WHERE tops.total_sold_tickets in (SELECT MAX(second_max.total_sold_tickets)\
																  FROM ({}) as second_max\
								   		 						  WHERE second_max.total_sold_tickets NOT IN (SELECT MAX(max_tickets.total_sold_tickets)\
																  										      FROM ({}) as max_tickets))"
	
	second_top_destination_q_month = second_top_destination_q.format(monthly_sub_q, monthly_sub_q, monthly_sub_q)
	second_top_destination_q_year = second_top_destination_q.format(yearly_sub_q, yearly_sub_q, yearly_sub_q)

	cursor.execute(second_top_destination_q_month, (airline_name, airline_name, airline_name))
	second_top_city_month = cursor.fetchall()
	# if second_top_city == None:
	# 	return render_template('view_top_destination.html', airline=airline_name, top_des=top_3_destination)

	#print("second top city:", second_top_city)
	
	for line in second_top_city_month:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_month.append(top_city_dict)


	cursor.execute(second_top_destination_q_year, (airline_name, airline_name, airline_name))
	second_top_city_year = cursor.fetchall()

	for line in second_top_city_year:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_year.append(top_city_dict)


	found_all_month += len(second_top_city_month)
	found_all_year += len(second_top_city_year)

	while found_all_year > 3:
		top_3_destination_year.pop()
		found_all_year.pop()

	while found_all_month > 3:
		top_3_destination_month.pop()
		found_all_month.pop()

	print("2nd q, month:", top_3_destination_month)
	print("2nd q, year:", top_3_destination_year)

	if found_all_year == 3 and found_all_month == 3:
		#print("here", top_3_destination)
		return render_template('view_top_destination.html', airline=airline_name, top_des_m=top_3_destination_month, top_des_y=top_3_destination_year)


	third_top_destination_q =  "SELECT tops.City, tops.total_sold_tickets\
								FROM ({}) as tops\
								WHERE tops.total_sold_tickets in (SELECT MAX(third_max.total_sold_tickets)\
																  FROM ({}) as third_max\
								   		 						  WHERE third_max.total_sold_tickets <  (SELECT MAX(second_max.total_sold_tickets)\
																  										 FROM ({}) as second_max\
																  										 WHERE second_max.total_sold_tickets NOT IN (SELECT MAX(top_max.total_sold_tickets)\
																  																					FROM ({}) as top_max)))"



	third_top_destination_q_month = third_top_destination_q.format(monthly_sub_q, monthly_sub_q, monthly_sub_q, monthly_sub_q)
	third_top_destination_q_year = third_top_destination_q.format(yearly_sub_q, yearly_sub_q, yearly_sub_q, yearly_sub_q)

	cursor.execute(third_top_destination_q_month, (airline_name, airline_name, airline_name, airline_name))
	third_top_city_month = cursor.fetchall()

	cursor.execute(third_top_destination_q_year, (airline_name, airline_name, airline_name, airline_name))
	third_top_city_year = cursor.fetchall()


	# if third_top_city == None:
	# 	return render_template('view_top_destination.html', airline=airline_name, top_des=top_3_destination)

	for line in third_top_city_month:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_month.append(top_city_dict)


	for line in third_top_city_year:
		top_city_dict = {}
		top_city_dict["City"] = line["City"]
		top_city_dict["freq"] = line["total_sold_tickets"]
		top_3_destination_year.append(top_city_dict)


	found_all_month += len(third_top_city_month)
	found_all_year += len(third_top_city_year)


	while found_all_month > 3:
		top_3_destination_month.pop()
		found_all_month.pop()

	while found_all_year > 3:
		top_3_destination_year.pop()
		found_all_year.pop()

	cursor.close()

	print("3rd q, month:", top_3_destination_month)
	print("3rd q, year:", top_3_destination_year)

	return render_template('view_top_destination.html', airline=airline_name, top_des_m=top_3_destination_month, top_des_y=top_3_destination_year)


	#############


@app.route('/freq_customers')
def view_frequent_customers():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	username = session['username']
	cursor = conn.cursor()
    # find most frequent customer's name within the last year for staff's airline
	query0 = 'SELECT name\
			FROM ((SELECT distinct email\
					FROM staff, ticket\
					WHERE username = %s and staff.airline_name = ticket.airline_name and date(departure_date_time)\
						>= date_add(current_date, interval -1 year) and date(departure_date_time) <= current_date)\
					except\
					(SELECT distinct A.email\
					FROM (SELECT email, count(ticket_id) as bought_tickets\
							FROM staff, ticket\
							WHERE username = %s and staff.airline_name = ticket.airline_name and date(departure_date_time)\
								>= date_add(current_date, interval -1 year) and date(departure_date_time) <= current_date\
							group by email) as A,\
							(SELECT email, count(ticket_id) as bought_tickets\
							FROM staff, ticket\
							WHERE username = %s and staff.airline_name = ticket.airline_name and date(departure_date_time)\
								>= date_add(current_date, interval -1 year) and date(departure_date_time) <= current_date\
							group by email) as B\
					WHERE A.bought_tickets < B.bought_tickets)) as M, customer\
				WHERE customer.email = M.email'
	cursor.execute(query0, (username,username,username))
	data0 = cursor.fetchone()
	error=None
	if not data0:
		error='No customers have taken any flights from your airline...'
		return render_template('frequent_customers.html',error=error)
	most_freq_name = data0['name']
	session['most_freq_name'] = most_freq_name    # make sure to pop this key from session when logging out
	cursor.close()
	return render_template('frequent_customers.html', most_freq_name=most_freq_name)

@app.route('/list_flights', methods=['GET','POST'])
def list_flights():


	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)

	cursor = conn.cursor()


	username = session['username']
	customer_email = request.form['email']
	most_freq_name = session['most_freq_name']

	airline_query = 'SELECT Airline_name FROM Staff WHERE Username = %s';
	cursor.execute(airline_query, (username))
	airline_name = cursor.fetchone()["Airline_name"]

	# retrieve list of past flights that target customer has been on for your airline
	query1 = 'SELECT F.Flight_num, T.Airline_name, F.Departure_date_time\
				FROM Flight as F, Ticket as T, Customer as C\
				WHERE C.Email = %s AND\
					  T.Email = C.Email AND\
					  T.Airline_name = F.Airline_name AND\
					  T.Departure_date_time = F.Departure_date_time AND\
					  T.Flight_num = F.Flight_num AND\
					  F.Departure_date_time < CURRENT_TIMESTAMP AND\
					  T.Airline_name = %s'
	cursor.execute(query1, (customer_email, airline_name))
	data1 = cursor.fetchall()
	cursor.close()
	return render_template('frequent_customers.html', most_freq_name=most_freq_name, data=data1)

@app.route('/view_reports')
def view_reports():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	# retrieve total sales within the past month
	cursor = conn.cursor()
	username = session['username']
	query0 = 'SELECT count(ticket_id) as total_month \
				FROM Ticket, staff \
				WHERE date_add(current_date, interval -1 month) <= date(purchase_date_time) and date(purchase_date_time) \
					<= current_date and username = %s and staff.airline_name = ticket.airline_name'
	cursor.execute(query0, (username))
	data0 = cursor.fetchone()
	# retrieve total sales within the past year
	query1 = 'SELECT count(ticket_id) as total_year \
				FROM Ticket, staff \
				WHERE date_add(current_date, interval -1 year) <= date(purchase_date_time) and date(purchase_date_time) \
					<= current_date and username = %s and staff.airline_name = ticket.airline_name'
	cursor.execute(query1, (username))
	data1 = cursor.fetchone()
	if data0:
		past_month_sales = data0['total_month']
	else:
		past_month_sales = 0
	if data1:
		past_year_sales = data1['total_year']
	else:
		past_year_sales = 0
    
	session['past_month_sales'] = past_month_sales
	session['past_year_sales'] = past_year_sales
	return render_template('view_reports.html', month=past_month_sales, year=past_year_sales)

@app.route('/report_results', methods=['GET','POST'])
def report_results():

	if "username" not in session:
		error = "You need to be logged in as a staff to visit this page"
		return render_template('staff_login.html', error=error)


	cursor = conn.cursor()
	username = session['username']
	past_month_sales = session['past_month_sales']   # make sure to pop key from session when logging out
	past_year_sales = session['past_year_sales']    # make sure to pop key from session when logging out
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	# month-wise table of total sales within start and end dates
	query = 'SELECT month(date(purchase_date_time)) as month, count(ticket_id) as total_sold \
			FROM Ticket, staff\
			WHERE %s <= date(purchase_date_time) and date(purchase_date_time)\
				<= %s and username = %s and staff.airline_name = ticket.airline_name\
			group by month'
	cursor.execute(query,(start_date,end_date,username))
	data = cursor.fetchall()
	cursor.close()
	return render_template('view_reports.html', month=past_month_sales, year=past_year_sales, data=data, start=start_date,end=end_date, msg=1)



app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)







