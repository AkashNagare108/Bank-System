
from flask import Flask,request,render_template,url_for,session,redirect,flash
import mysql.connector

app=Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/customer",methods=['POST','GET'])
def customer():
    mydb=mysql.connector.connect(host="localhost",user="root",password="",database="bank_system")
    cur=mydb.cursor()
    cur.execute("SELECT * FROM customer_detail")
    data=cur.fetchall()
    return render_template("customer.html",value=data)



@app.route("/transaction", methods=['POST', 'GET'])
def transaction():
    if request.method == 'POST':
        accountno = request.form['acc_num']
        to_accountno = request.form['to_account_no']
        amount = request.form['amount']
        
            # return "Cannot transfer money to the same account"

        mydb = mysql.connector.connect(host="localhost", user="root", password="", database="bank_system")
        cur = mydb.cursor()

        try:
            cur.execute("SELECT balance FROM customer_detail WHERE accountno = %s", (accountno,))
            sender_balance = cur.fetchone()[0]
            if float(amount) > sender_balance:
                flash("Insufficient Balance",'danger')
            elif float(amount)==0:
                flash("Amount should be greater than zero",'danger')

            elif to_accountno != accountno:
                # Check if there's enough balance before making the transaction
                if float(amount) > sender_balance:
                    flash("Insufficient Balance", 'danger')
                else:
                    # Insert into transaction_history table
                    cur.execute("INSERT INTO transaction_history (sender_account_no, receiver_account_no, amount,status) VALUES (%s, %s, %s,%s)", (accountno, to_accountno, amount,"Success"))

                    # Debit from the sender's account
                    cur.execute("UPDATE customer_detail SET balance = balance - %s WHERE accountno = %s", (amount, accountno))

                    # Credit to the receiver's account
                    cur.execute("UPDATE customer_detail SET balance = balance + %s WHERE accountno = %s", (amount, to_accountno))

                    mydb.commit()
                    flash("Transaction Successful",'success')
                    # return redirect(url_for('history',success='True'))
            else:
                cur.execute("INSERT INTO transaction_history (sender_account_no, receiver_account_no, amount, status) VALUES (%s, %s, %s, %s)", (accountno, to_accountno, amount, "Failed"))
                mydb.commit()
                flash("Transaction Failed: money cannot transfer between same account numbers",'danger')
                # return redirect(url_for('history', success='False'))

        except mysql.connector.Error as err:
                print(f"Error: {err}")

        finally:
            cur.close()
            mydb.close()
        return redirect(url_for('history'))

    elif 'accountno' in request.args:
        accountno = request.args['accountno']
        balance = request.args['balance']

        mydb = mysql.connector.connect(host="localhost", user="root", password="", database="bank_system")
        cur = mydb.cursor()
        cur.execute("SELECT accountno FROM customer_detail")
        account_numbers = [row[0] for row in cur.fetchall()]

        return render_template("transaction.html", accountno=accountno, balance=balance, account_numbers=account_numbers)

    else:
        return "Account number or balance not provided in URL"


@app.route("/history",methods=['POST','GET'])
def history():
    mydb=mysql.connector.connect(host="localhost",user="root",password="",database="bank_system")
    cur=mydb.cursor()
    cur.execute("SELECT * FROM transaction_history")
    data=cur.fetchall()
    success = request.args.get('success', None)
    return render_template("history.html",value=data,success=success)

if __name__=="__main__":
    app.debug=True
    app.run()
    