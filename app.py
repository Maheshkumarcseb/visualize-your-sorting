from flask import Flask, render_template, request,jsonify, redirect, url_for, flash, session
import mysql.connector
import copy
import random

app = Flask(__name__)
app.secret_key = "12345"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",  
        database="flask_users"
    )


@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        account = cursor.fetchone()

        if account:
            msg = "User already registered! Please try a different email."
        else:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()
            flash("Signup successful! Please login.", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("login"))

        cursor.close()
        conn.close()

    return render_template("signup.html", msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            msg = "Incorrect email or password!"

    return render_template("login.html", msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/features')
def features():
    if 'loggedin' in session:
        return render_template('features.html', username=session['username'])
    flash('Please log in to access features.', 'warning')
    return redirect(url_for('login'))

@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DATABASE();")
        db_name = cur.fetchone()
        cur.close()
        conn.close()
        return f"✅ Connected successfully to database: {db_name}"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

@app.route('/sorting_analyzer', methods=['GET', 'POST'])
def sorting_analyzer():
    if 'loggedin' not in session:
        flash("Please login first to access the Sorting Analyzer.", "warning")
        return redirect(url_for('login'))

    result = None
    if request.method == 'POST':
        numbers = request.form['numbers']  # Example: comma-separated "5,2,8,1"
        try:
            numbers_list = [int(x.strip()) for x in numbers.split(',')]
            result = sorted(numbers_list)  # Simple sorting logic
        except ValueError:
            flash("Please enter valid integers separated by commas.", "error")

    return render_template("sorting_analyzer.html", result=result)

@app.route("/generate_array/<int:size>")
def generate_array(size):
    array = [random.randint(10, 100) for _ in range(size)]
    return jsonify(array)

def bubble_sort(arr):
    steps = []
    n = len(arr)
    for i in range(n-1):
        for j in range(n-i-1):
            steps.append((copy.deepcopy(arr), [j, j+1]))
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                steps.append((copy.deepcopy(arr), [j, j+1]))
    steps.append((copy.deepcopy(arr), []))
    return steps

def selection_sort(arr):
    steps = []
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            steps.append((copy.deepcopy(arr), [i, j]))
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        steps.append((copy.deepcopy(arr), [i, min_idx]))
    steps.append((copy.deepcopy(arr), []))
    return steps

def insertion_sort(arr):
    steps = []
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            steps.append((copy.deepcopy(arr), [j, j+1]))
            j -= 1
        arr[j+1] = key
        steps.append((copy.deepcopy(arr), [j+1]))
    steps.append((copy.deepcopy(arr), []))
    return steps

def merge_sort_steps(arr):
    steps = []
    def merge_sort(arr, left, right):
        if left >= right:
            return
        mid = (left+right)//2
        merge_sort(arr, left, mid)
        merge_sort(arr, mid+1, right)
        merge(arr, left, mid, right)

    def merge(arr, left, mid, right):
        L = arr[left:mid+1]
        R = arr[mid+1:right+1]
        i=j=0
        k=left
        while i<len(L) and j<len(R):
            if L[i]<=R[j]:
                arr[k]=L[i]; i+=1
            else:
                arr[k]=R[j]; j+=1
            steps.append((copy.deepcopy(arr), [k]))
            k+=1
        while i<len(L):
            arr[k]=L[i]; i+=1; k+=1
            steps.append((copy.deepcopy(arr), [k]))
        while j<len(R):
            arr[k]=R[j]; j+=1; k+=1
            steps.append((copy.deepcopy(arr), [k]))

    merge_sort(arr,0,len(arr)-1)
    steps.append((copy.deepcopy(arr), []))
    return steps

def quick_sort_steps(arr):
    steps = []
    def quick_sort(arr, low, high):
        if low<high:
            pi = partition(arr, low, high)
            quick_sort(arr, low, pi-1)
            quick_sort(arr, pi+1, high)

    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            steps.append((copy.deepcopy(arr), [j, high]))
            if arr[j]<pivot:
                i+=1
                arr[i], arr[j]=arr[j], arr[i]
                steps.append((copy.deepcopy(arr), [i, j]))
        arr[i+1], arr[high]=arr[high], arr[i+1]
        steps.append((copy.deepcopy(arr), [i+1, high]))
        return i+1

    quick_sort(arr,0,len(arr)-1)
    steps.append((copy.deepcopy(arr), []))
    return steps

def heap_sort_steps(arr):
    steps = []
    n = len(arr)
    def heapify(n,i):
        largest=i
        l=2*i+1
        r=2*i+2
        if l<n and arr[l]>arr[largest]:
            largest=l
        if r<n and arr[r]>arr[largest]:
            largest=r
        if largest!=i:
            arr[i], arr[largest]=arr[largest], arr[i]
            steps.append((copy.deepcopy(arr), [i, largest]))
            heapify(n, largest)

    for i in range(n//2-1, -1, -1):
        heapify(n, i)
    for i in range(n-1, 0, -1):
        arr[i], arr[0]=arr[0], arr[i]
        steps.append((copy.deepcopy(arr), [0, i]))
        heapify(i, 0)
    steps.append((copy.deepcopy(arr), []))
    return steps


@app.route("/start_sort", methods=["POST"])
def start_sort():
    data = request.json
    array = data['array']
    algorithm = data.get('algorithm','bubble')

    if algorithm=='bubble':
        steps = bubble_sort(array)
    elif algorithm=='selection':
        steps = selection_sort(array)
    elif algorithm=='insertion':
        steps = insertion_sort(array)
    elif algorithm=='merge':
        steps = merge_sort_steps(array)
    elif algorithm=='quick':
        steps = quick_sort_steps(array)
    elif algorithm=='heap':
        steps = heap_sort_steps(array)
    else:
        steps = bubble_sort(array)

    json_steps = [{'array': s[0], 'indices': s[1]} for s in steps]
    return jsonify(json_steps)

if __name__ == '__main__':
    app.run(debug=True)
