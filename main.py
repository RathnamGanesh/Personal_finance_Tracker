from flask import Flask, render_template, request, redirect
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import os
from datetime import date, datetime

app = Flask(__name__)
transactions = []

# Load existing data
try:
    with open("transactions.json", "r") as f:
        transactions = json.load(f)
except FileNotFoundError:
    transactions = []

def save_data():
    with open("transactions.json", "w") as f:
        json.dump(transactions, f)

def calculate_balance():
    balance = 0
    for t in transactions:
        balance += t["amount"] if t["type"] == "Income" else -t["amount"]
    return balance

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            category = request.form["category"].strip()
            t_type = request.form["type"]
            if category:
                transactions.append({
                    "amount": amount,
                    "category": category,
                    "type": t_type,
                    "date": str(date.today())
                })
                save_data()
        except:
            pass
        return redirect("/")
    return render_template("index.html", transactions=transactions, balance=calculate_balance())

@app.route("/clear_month", methods=["POST"])
def clear_month():
    month = int(request.form["month"])
    year = int(request.form["year"])
    global transactions
    transactions = [
        t for t in transactions
        if datetime.strptime(t["date"], "%Y-%m-%d").month != month or
           datetime.strptime(t["date"], "%Y-%m-%d").year != year
    ]
    save_data()
    return redirect("/")

@app.route("/graph")
def graph():
    category_totals = defaultdict(float)
    for t in transactions:
        if t["type"] == "Expense":
            category_totals[t["category"]] += t["amount"]

    if not os.path.exists("static"):
        os.makedirs("static")

    categories = list(category_totals.keys())
    values = list(category_totals.values())

    plt.figure(figsize=(6, 4))
    plt.bar(categories, values, color="skyblue")
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.savefig("static/graph.png")
    plt.close()

    return render_template("graph.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
