import sys
import os
import threading
import webbrowser
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import date


def get_base_path():
    """Get the base path for bundled resources (templates, static, sql)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_app_path():
    """Get the application path for user data (database)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


base_path = get_base_path()
app_path = get_app_path()

app = Flask(__name__,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

DB_PATH = os.path.join(app_path, "data", "store.db")


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    """Initialize database from init.sql if the DB file does not exist yet."""
    if os.path.exists(DB_PATH):
        return
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    init_sql_path = os.path.join(base_path, "docker", "init.sql")
    if os.path.exists(init_sql_path):
        with open(init_sql_path, "r", encoding="utf-8") as f:
            db.executescript(f.read())
    db.close()


# --- ID generators ---

def generate_product_id(cur):
    cur.execute("SELECT MAX(PID) FROM Product")
    result = cur.fetchone()
    if result[0] is None:
        return 'P001'
    return 'P' + str(int(result[0][1:]) + 1).zfill(3)


def generate_customer_id(cur):
    cur.execute("SELECT MAX(CID) FROM Customer")
    result = cur.fetchone()
    if result[0] is None:
        return 'C001'
    return 'C' + str(int(result[0][1:]) + 1).zfill(3)


def generate_dealer_id(cur):
    cur.execute("SELECT MAX(DID) FROM Dealer")
    result = cur.fetchone()
    if result[0] is None:
        return 'D001'
    return 'D' + str(int(result[0][1:]) + 1).zfill(3)


def generate_salesperson_id(cur):
    cur.execute("SELECT MAX(SID) FROM Salesperson")
    result = cur.fetchone()
    if result[0] is None:
        return 'S001'
    return 'S' + str(int(result[0][1:]) + 1).zfill(3)


def generate_invoice_id(cur):
    cur.execute("SELECT MAX(InvoiceID) FROM Invoices")
    result = cur.fetchone()
    if result[0] is None:
        return 'I00001'
    return 'I' + str(int(result[0][1:]) + 1).zfill(5)


def generate_purchase_id(cur):
    cur.execute("SELECT MAX(PurchaseID) FROM Purchases")
    result = cur.fetchone()
    if result[0] is None:
        return 'U00001'
    return 'U' + str(int(result[0][1:]) + 1).zfill(5)


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')


# --- Products ---

@app.route('/products/add', methods=['GET', 'POST'])
def product_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            pid = generate_product_id(cur)
            pname = request.form['pname']
            unit1 = request.form['unit1']
            unit2 = request.form.get('unit2', '').strip() or None
            conversion_factor = request.form.get('conversion_factor', '').strip()
            conversion_factor = float(conversion_factor) if conversion_factor else None
            quantity = float(request.form['quantity'])
            price = int(request.form['price'])

            if unit2 and not conversion_factor:
                flash('Phải nhập hệ số quy đổi khi có đơn vị phụ!', 'error')
                cur.close()
                db.close()
                return redirect(url_for('product_add'))

            cf_sql = conversion_factor if conversion_factor else 'NULL'
            unit2_sql = f"'{unit2}'" if unit2 else 'NULL'
            cur.execute(f"INSERT INTO Product (PID, PName, Unit1, Unit2, ConversionFactor, Quantity, Price) VALUES ('{pid}', '{pname}', '{unit1}', {unit2_sql}, {cf_sql}, {quantity}, {price})")
            db.commit()
            flash('Thêm sản phẩm thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('product_add'))
    pid = generate_product_id(cur)
    cur.close()
    db.close()
    return render_template('products/add.html', pid=pid)


@app.route('/products')
def product_list():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT PID, PName, Unit1, Unit2, ConversionFactor, Price FROM Product ORDER BY PName")
    products = cur.fetchall()
    cur.close()
    db.close()
    return render_template('products/list.html', products=products)


@app.route('/products/stock')
def product_stock():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT PID, PName, Unit1, Quantity FROM Product ORDER BY PName")
    products = cur.fetchall()
    cur.close()
    db.close()
    return render_template('products/stock.html', products=products)


@app.route('/products/update', methods=['GET', 'POST'])
def product_update():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            pid = request.form['pid']
            pname = request.form['pname']
            unit1 = request.form['unit1']
            unit2 = request.form.get('unit2', '').strip() or None
            conversion_factor = request.form.get('conversion_factor', '').strip()
            conversion_factor = float(conversion_factor) if conversion_factor else None
            quantity = float(request.form['quantity'])
            price = int(request.form['price'])

            if unit2 and not conversion_factor:
                flash('Phải nhập hệ số quy đổi khi có đơn vị phụ!', 'error')
                cur.close()
                db.close()
                return redirect(url_for('product_update', pid=pid))

            cf_sql = conversion_factor if conversion_factor else 'NULL'
            unit2_sql = f"'{unit2}'" if unit2 else 'NULL'
            cur.execute(f"UPDATE Product SET PName='{pname}', Unit1='{unit1}', Unit2={unit2_sql}, ConversionFactor={cf_sql}, Quantity={quantity}, Price={price} WHERE PID='{pid}'")
            db.commit()
            flash('Cập nhật sản phẩm thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('product_update', pid=request.form['pid']))
    pid = request.args.get('pid')
    product = None
    if pid:
        cur.execute(f"SELECT PID, PName, Unit1, Unit2, ConversionFactor, Quantity, Price FROM Product WHERE PID='{pid}'")
        product = cur.fetchone()
        if not product:
            flash('Không tìm thấy mã sản phẩm!', 'error')
    cur.close()
    db.close()
    return render_template('products/update.html', pid=pid, product=product)


@app.route('/products/delete', methods=['POST'])
def product_delete():
    pid = request.form.get('pid')
    redirect_to = request.form.get('redirect_to', url_for('product_list'))
    if pid:
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(f"DELETE FROM Product WHERE PID='{pid}'")
            db.commit()
            flash('Xóa sản phẩm thành công', 'success')
        except Exception:
            flash('Không thể xóa sản phẩm (có thể đang được sử dụng trong hóa đơn/phiếu nhập)', 'error')
        finally:
            cur.close()
            db.close()
    return redirect(redirect_to)


# --- Customers ---

@app.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            cid = generate_customer_id(cur)
            cname = request.form['cname']
            address = request.form['address']
            idnumber = request.form['idnumber']
            phone = request.form['phone']
            cur.execute(f"INSERT INTO Customer (CID, CName, Address, IDNumber, Phone) VALUES ('{cid}', '{cname}', '{address}', '{idnumber}', '{phone}')")
            db.commit()
            flash('Thêm khách hàng thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('customer_add'))
    cid = generate_customer_id(cur)
    cur.close()
    db.close()
    return render_template('customers/add.html', cid=cid)


@app.route('/customers/update', methods=['GET', 'POST'])
def customer_update():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            cid = request.form['cid']
            cname = request.form['cname']
            address = request.form['address']
            idnumber = request.form['idnumber']
            phone = request.form['phone']
            cur.execute(f"UPDATE Customer SET CName='{cname}', Address='{address}', IDNumber='{idnumber}', Phone='{phone}' WHERE CID='{cid}'")
            db.commit()
            flash('Cập nhật khách hàng thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('customer_update', cid=request.form['cid']))
    cid = request.args.get('cid')
    customer = None
    if cid:
        cur.execute(f"SELECT * FROM Customer WHERE CID='{cid}'")
        customer = cur.fetchone()
        if not customer:
            flash('Không tìm thấy mã khách hàng!', 'error')
    cur.close()
    db.close()
    return render_template('customers/update.html', cid=cid, customer=customer)


@app.route('/customers/delete', methods=['POST'])
def customer_delete():
    cid = request.form.get('cid')
    redirect_to = request.form.get('redirect_to', url_for('customer_display'))
    if cid:
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(f"DELETE FROM Customer WHERE CID='{cid}'")
            db.commit()
            flash('Xóa khách hàng thành công', 'success')
        except Exception:
            flash('Không thể xóa khách hàng (có thể đang được sử dụng trong hóa đơn)', 'error')
        finally:
            cur.close()
            db.close()
    return redirect(redirect_to)


@app.route('/customers/display')
def customer_display():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cur = db.cursor()

    cur.execute(f"SELECT COUNT(*) FROM Customer WHERE CName LIKE '%{q}%'")
    total_customers = cur.fetchone()[0]

    cur.execute(f"SELECT * FROM Customer WHERE CName LIKE '%{q}%' LIMIT {per_page} OFFSET {offset}")
    customers = cur.fetchall()

    cur.close()
    db.close()

    total_pages = (total_customers + per_page - 1) // per_page

    return render_template('customers/display.html', customers=customers, q=q, page=page, total_pages=total_pages)


# --- Dealers ---

@app.route('/dealers/add', methods=['GET', 'POST'])
def dealer_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            did = generate_dealer_id(cur)
            dname = request.form['dname']
            cur.execute(f"INSERT INTO Dealer (DID, DName) VALUES ('{did}', '{dname}')")
            db.commit()
            flash('Thêm nhà cung cấp thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('dealer_add'))
    did = generate_dealer_id(cur)
    cur.close()
    db.close()
    return render_template('dealers/add.html', did=did)


@app.route('/dealers/update', methods=['GET', 'POST'])
def dealer_update():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            did = request.form['did']
            dname = request.form['dname']
            cur.execute(f"UPDATE Dealer SET DName='{dname}' WHERE DID='{did}'")
            db.commit()
            flash('Cập nhật nhà cung cấp thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('dealer_update', did=request.form['did']))
    did = request.args.get('did')
    dealer = None
    if did:
        cur.execute(f"SELECT * FROM Dealer WHERE DID='{did}'")
        dealer = cur.fetchone()
        if not dealer:
            flash('Không tìm thấy mã nhà cung cấp!', 'error')
    cur.close()
    db.close()
    return render_template('dealers/update.html', did=did, dealer=dealer)


@app.route('/dealers/delete', methods=['POST'])
def dealer_delete():
    did = request.form.get('did')
    redirect_to = request.form.get('redirect_to', url_for('dealer_display'))
    if did:
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(f"DELETE FROM Dealer WHERE DID='{did}'")
            db.commit()
            flash('Xóa nhà cung cấp thành công', 'success')
        except Exception:
            flash('Không thể xóa nhà cung cấp (có thể đang được sử dụng trong phiếu nhập)', 'error')
        finally:
            cur.close()
            db.close()
    return redirect(redirect_to)


@app.route('/dealers/display')
def dealer_display():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cur = db.cursor()

    cur.execute(f"SELECT COUNT(*) FROM Dealer WHERE DName LIKE '%{q}%' OR DID LIKE '%{q}%'")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT * FROM Dealer WHERE DName LIKE '%{q}%' OR DID LIKE '%{q}%' LIMIT {per_page} OFFSET {offset}")
    dealers = cur.fetchall()

    cur.close()
    db.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template('dealers/display.html', dealers=dealers, q=q, page=page, total_pages=total_pages)


# --- Salespersons ---

@app.route('/salespersons/add', methods=['GET', 'POST'])
def salesperson_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            sid = generate_salesperson_id(cur)
            sname = request.form['sname']
            phone = request.form['phone']
            cur.execute(f"INSERT INTO Salesperson (SID, SName, Phone) VALUES ('{sid}', '{sname}', '{phone}')")
            db.commit()
            flash('Thêm nhân viên thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('salesperson_add'))
    sid = generate_salesperson_id(cur)
    cur.close()
    db.close()
    return render_template('salespersons/add.html', sid=sid)


@app.route('/salespersons/update', methods=['GET', 'POST'])
def salesperson_update():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            sid = request.form['sid']
            sname = request.form['sname']
            phone = request.form['phone']
            cur.execute(f"UPDATE Salesperson SET SName='{sname}', Phone='{phone}' WHERE SID='{sid}'")
            db.commit()
            flash('Cập nhật nhân viên thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('salesperson_update', sid=request.form['sid']))
    sid = request.args.get('sid')
    salesperson = None
    if sid:
        cur.execute(f"SELECT * FROM Salesperson WHERE SID='{sid}'")
        salesperson = cur.fetchone()
        if not salesperson:
            flash('Không tìm thấy nhân viên!', 'error')
    cur.close()
    db.close()
    return render_template('salespersons/update.html', sid=sid, salesperson=salesperson)


@app.route('/salespersons/delete', methods=['POST'])
def salesperson_delete():
    sid = request.form.get('sid')
    redirect_to = request.form.get('redirect_to', url_for('salesperson_display'))
    if sid:
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(f"DELETE FROM Salesperson WHERE SID='{sid}'")
            db.commit()
            flash('Xóa nhân viên thành công', 'success')
        except Exception:
            flash('Không thể xóa nhân viên (có thể đang được sử dụng trong hóa đơn)', 'error')
        finally:
            cur.close()
            db.close()
    return redirect(redirect_to)


@app.route('/salespersons/display')
def salesperson_display():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cur = db.cursor()

    cur.execute(f"SELECT COUNT(*) FROM Salesperson WHERE SName LIKE '%{q}%' OR SID LIKE '%{q}%'")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT * FROM Salesperson WHERE SName LIKE '%{q}%' OR SID LIKE '%{q}%' LIMIT {per_page} OFFSET {offset}")
    salespersons = cur.fetchall()

    cur.close()
    db.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template('salespersons/display.html', salespersons=salespersons, q=q, page=page, total_pages=total_pages)


# --- Invoices ---

@app.route('/invoices/add', methods=['GET', 'POST'])
def invoice_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            invoice_id = generate_invoice_id(cur)
            cid = request.form['cid']
            salesperson_id = request.form['salesperson_id']

            cur.execute("SELECT CID FROM Customer")
            if (cid,) not in cur.fetchall():
                flash("Khách hàng không tồn tại", 'error')
                return redirect(url_for('invoice_add'))

            cur.execute(f"SELECT SID FROM Salesperson WHERE SID='{salesperson_id}'")
            if not cur.fetchone():
                flash("Nhân viên bán hàng không tồn tại", 'error')
                return redirect(url_for('invoice_add'))

            pids = request.form.getlist('pid[]')
            qtys = request.form.getlist('qty[]')
            prices = request.form.getlist('price[]')
            units = request.form.getlist('unit[]')
            line_discounts = request.form.getlist('discount[]')
            order_discount = float(request.form.get('order_discount', 0) or 0)

            if not pids or all(p == '' for p in pids):
                flash('Không có mục nào', 'error')
                return redirect(url_for('invoice_add'))

            # Load product info for stock validation
            cur.execute("SELECT PID, Quantity, Unit1, Unit2, ConversionFactor FROM Product")
            products = {}
            for row in cur.fetchall():
                products[row[0]] = {
                    'quantity': float(row[1]),
                    'unit1': row[2],
                    'unit2': row[3],
                    'cf': float(row[4]) if row[4] else None
                }

            subtotal = 0
            lines = []
            # Track cumulative deductions per product (in Unit1)
            deductions = {}
            for i in range(len(pids)):
                if pids[i] == '':
                    continue
                pid = pids[i]
                qty = float(qtys[i])
                price = int(prices[i])
                selected_unit = units[i]
                line_disc_amt = float(line_discounts[i]) if i < len(line_discounts) and line_discounts[i] else 0

                if pid not in products:
                    flash(f'Không tìm thấy sản phẩm {pid}', 'error')
                    return redirect(url_for('invoice_add'))

                prod = products[pid]

                # Convert quantity to Unit1 for stock check
                if selected_unit == prod['unit1']:
                    qty_in_unit1 = qty
                elif selected_unit == prod['unit2'] and prod['cf']:
                    qty_in_unit1 = qty / prod['cf']
                else:
                    flash(f'Đơn vị không hợp lệ cho sản phẩm {pid}', 'error')
                    return redirect(url_for('invoice_add'))

                deductions[pid] = deductions.get(pid, 0) + qty_in_unit1

                if deductions[pid] > prod['quantity']:
                    flash(f'Số lượng tồn kho không đủ cho sản phẩm {pid}!', 'error')
                    return redirect(url_for('invoice_add'))

                line_total = price * qty - line_disc_amt
                subtotal += line_total
                lines.append((pid, selected_unit, qty, price, qty_in_unit1, line_disc_amt))

            total_amt = subtotal - order_discount

            cur.execute(f"INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES ('{invoice_id}', '{cid}', '{salesperson_id}', '{date.today()}', {order_discount}, {total_amt})")
            for pid, selected_unit, qty, price, qty_in_unit1, line_disc_amt in lines:
                cur.execute(f"INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES ('{invoice_id}', '{pid}', '{selected_unit}', {qty}, {price}, {line_disc_amt})")
                cur.execute(f"UPDATE Product SET Quantity = Quantity - {qty_in_unit1} WHERE PID = '{pid}'")
            db.commit()
            return redirect(url_for('invoice_confirm', invoice_id=invoice_id))
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('invoice_add'))

    invoice_id = generate_invoice_id(cur)
    cur.close()
    db.close()
    return render_template('invoices/add.html', invoice_id=invoice_id)


@app.route('/invoices/confirm')
def invoice_confirm():
    invoice_id = request.args.get('invoice_id')
    if not invoice_id:
        return redirect(url_for('invoice_add'))
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM Invoices WHERE InvoiceID='{invoice_id}'")
    invoice = cur.fetchone()
    if not invoice:
        flash('Không tìm thấy hóa đơn', 'error')
        cur.close()
        db.close()
        return redirect(url_for('invoice_add'))
    cname = ''
    caddress = ''
    sname = ''
    cur.execute(f"SELECT CName, Address FROM Customer WHERE CID='{invoice[1]}'")
    row = cur.fetchone()
    cname = row[0] if row else '(đã xóa)'
    caddress = row[1] if row else ''
    if invoice[2]:
        cur.execute(f"SELECT SName FROM Salesperson WHERE SID='{invoice[2]}'")
        srow = cur.fetchone()
        sname = srow[0] if srow else ''
    cur.execute(f"SELECT Product.PID, PName, InvoiceDetails.SelectedUnit, InvoiceDetails.Quantity, InvoiceDetails.Price, InvoiceDetails.Discount FROM InvoiceDetails, Product WHERE InvoiceDetails.InvoiceID='{invoice_id}' AND InvoiceDetails.PID = Product.PID")
    items = cur.fetchall()
    # items: (PID, PName, Unit, Qty, Price, DiscountAmt)
    subtotal = sum(float(item[3]) * float(item[4]) - float(item[5] or 0) for item in items)
    order_discount = float(invoice[5] or 0)  # Invoices.Discount column (amount)
    items_total = subtotal - order_discount
    cur.close()
    db.close()
    return render_template('invoices/confirm.html', invoice_id=invoice_id, invoice=invoice, cname=cname, caddress=caddress, sname=sname, items=items, subtotal=subtotal, order_discount=order_discount, items_total=items_total)


@app.route('/invoices/display')
def invoice_display():
    invoice_id = request.args.get('invoice_id')
    if invoice_id:
        db = get_db()
        cur = db.cursor()
        cur.execute(f"SELECT * FROM Invoices WHERE InvoiceID='{invoice_id}'")
        invoice = cur.fetchone()
        cname = None
        caddress = ''
        sname = ''
        items = []
        items_total = 0
        if not invoice:
            flash('Không tìm thấy hóa đơn', 'error')
        else:
            cur.execute(f"SELECT CName, Address FROM Customer WHERE CID='{invoice[1]}'")
            row = cur.fetchone()
            cname = row[0] if row else '(đã xóa)'
            caddress = row[1] if row else ''
            if invoice[2]:
                cur.execute(f"SELECT SName FROM Salesperson WHERE SID='{invoice[2]}'")
                srow = cur.fetchone()
                sname = srow[0] if srow else ''
            cur.execute(f"SELECT Product.PID, PName, InvoiceDetails.SelectedUnit, InvoiceDetails.Quantity, InvoiceDetails.Price, InvoiceDetails.Discount FROM InvoiceDetails, Product WHERE InvoiceDetails.InvoiceID='{invoice_id}' AND InvoiceDetails.PID = Product.PID")
            items = cur.fetchall()
            subtotal = sum(float(item[3]) * float(item[4]) - float(item[5] or 0) for item in items)
            order_discount = float(invoice[5] or 0)  # amount
            items_total = subtotal - order_discount
        cur.close()
        db.close()
        return render_template('invoices/display.html', invoice_id=invoice_id, invoice=invoice, cname=cname, caddress=caddress, sname=sname, items=items, subtotal=subtotal if invoice else 0, order_discount=order_discount if invoice else 0, items_total=items_total)

    q = request.args.get('q', '')
    customer_name = request.args.get('customer_name', '')
    salesperson_name = request.args.get('salesperson_name', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cur = db.cursor()

    where_clauses = [f"(Invoices.InvoiceID LIKE '%{q}%' OR Invoices.CID LIKE '%{q}%')"]
    if customer_name:
        where_clauses.append(f"Customer.CName LIKE '%{customer_name}%'")
    if salesperson_name:
        where_clauses.append(f"Salesperson.SName LIKE '%{salesperson_name}%'")
    if start_date:
        where_clauses.append(f"Invoices.InvoiceDate >= '{start_date}'")
    if end_date:
        where_clauses.append(f"Invoices.InvoiceDate <= '{end_date}'")

    where_sql = " AND ".join(where_clauses)
    join_sql = "LEFT JOIN Customer ON Invoices.CID = Customer.CID LEFT JOIN Salesperson ON Invoices.SalespersonID = Salesperson.SID"

    cur.execute(f"SELECT COUNT(*) FROM Invoices {join_sql} WHERE {where_sql}")
    total_invoices = cur.fetchone()[0]

    cur.execute(f"SELECT Invoices.InvoiceID, Invoices.CID, Customer.CName, Salesperson.SName, Invoices.InvoiceDate, Invoices.TotalAmt FROM Invoices {join_sql} WHERE {where_sql} ORDER BY Invoices.InvoiceDate DESC, Invoices.InvoiceID DESC LIMIT {per_page} OFFSET {offset}")
    invoices = cur.fetchall()

    cur.close()
    db.close()

    total_pages = (total_invoices + per_page - 1) // per_page

    return render_template('invoices/display.html', invoices=invoices, q=q, customer_name=customer_name, salesperson_name=salesperson_name, start_date=start_date, end_date=end_date, page=page, total_pages=total_pages)


@app.route('/invoices/summary', methods=['POST'])
def invoice_summary():
    invoice_ids = request.form.getlist('invoice_ids')
    if not invoice_ids:
        flash('Vui lòng chọn ít nhất một hóa đơn', 'error')
        return redirect(url_for('invoice_display'))

    db = get_db()
    cur = db.cursor()

    # Build safe IN clause
    id_list = ','.join(f"'{iid}'" for iid in invoice_ids)

    # Get invoice headers
    cur.execute(f"SELECT InvoiceID, CID, InvoiceDate, TotalAmt FROM Invoices WHERE InvoiceID IN ({id_list}) ORDER BY InvoiceDate")
    invoices = cur.fetchall()

    # Get all line items with product info
    cur.execute(f"SELECT InvoiceDetails.PID, Product.PName, Product.Unit1, Product.Unit2, InvoiceDetails.SelectedUnit, InvoiceDetails.Quantity, InvoiceDetails.Price, InvoiceDetails.Discount FROM InvoiceDetails JOIN Product ON InvoiceDetails.PID = Product.PID WHERE InvoiceDetails.InvoiceID IN ({id_list})")
    rows = cur.fetchall()

    cur.close()
    db.close()

    # Aggregate by product
    products = {}
    for pid, pname, unit1, unit2, selected_unit, qty, price, line_disc in rows:
        qty = float(qty)
        if pid not in products:
            products[pid] = {
                'pname': pname,
                'unit1': unit1,
                'unit2': unit2 or '',
                'qty_unit1': 0,
                'qty_unit2': 0,
                'total_amount': 0
            }
        if selected_unit == unit1:
            products[pid]['qty_unit1'] += qty
        else:
            products[pid]['qty_unit2'] += qty
        products[pid]['total_amount'] += price * qty - float(line_disc or 0)

    # Sort by PID
    product_list = sorted(products.items())
    grand_total = sum(p['total_amount'] for p in products.values())
    total_unit1 = sum(p['qty_unit1'] for p in products.values())
    total_unit2 = sum(p['qty_unit2'] for p in products.values())

    return render_template('invoices/summary.html',
                           invoices=invoices,
                           invoice_ids=invoice_ids,
                           product_list=product_list,
                           grand_total=grand_total,
                           total_unit1=total_unit1,
                           total_unit2=total_unit2)


@app.route('/invoices/delete', methods=['GET', 'POST'])
def invoice_delete():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        invoice_id = request.form['invoice_id']
        cur.execute(f"SELECT InvoiceID FROM Invoices WHERE InvoiceID='{invoice_id}'")
        if not cur.fetchone():
            flash('Không tìm thấy hóa đơn', 'error')
        else:
            # Restore stock before deleting
            cur.execute(f"SELECT PID, SelectedUnit, Quantity FROM InvoiceDetails WHERE InvoiceID='{invoice_id}'")
            details = cur.fetchall()
            cur.execute("SELECT PID, Unit1, Unit2, ConversionFactor FROM Product")
            prod_info = {}
            for row in cur.fetchall():
                prod_info[row[0]] = {'unit1': row[1], 'unit2': row[2], 'cf': float(row[3]) if row[3] else None}
            for pid, selected_unit, qty in details:
                qty = float(qty)
                prod = prod_info.get(pid)
                if prod:
                    if selected_unit == prod['unit1']:
                        qty_in_unit1 = qty
                    elif selected_unit == prod['unit2'] and prod['cf']:
                        qty_in_unit1 = qty / prod['cf']
                    else:
                        qty_in_unit1 = qty
                    cur.execute(f"UPDATE Product SET Quantity = Quantity + {qty_in_unit1} WHERE PID = '{pid}'")
            cur.execute(f"DELETE FROM Invoices WHERE InvoiceID='{invoice_id}'")
            db.commit()
            flash('Xóa hóa đơn thành công', 'success')
        cur.close()
        db.close()
        referrer = request.form.get('redirect_to', '')
        if referrer:
            return redirect(referrer)
        return redirect(url_for('invoice_delete'))
    return render_template('invoices/delete.html')


@app.route('/invoices/update/<invoice_id>', methods=['GET', 'POST'])
def invoice_update(invoice_id):
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            cid = request.form['cid']
            salesperson_id = request.form['salesperson_id']
            cur.execute(f"SELECT CID FROM Customer WHERE CID='{cid}'")
            if not cur.fetchone():
                flash("Khách hàng không tồn tại", 'error')
                cur.close()
                db.close()
                return redirect(url_for('invoice_update', invoice_id=invoice_id))

            cur.execute(f"SELECT SID FROM Salesperson WHERE SID='{salesperson_id}'")
            if not cur.fetchone():
                flash("Nhân viên bán hàng không tồn tại", 'error')
                cur.close()
                db.close()
                return redirect(url_for('invoice_update', invoice_id=invoice_id))

            # Restore old stock
            cur.execute(f"SELECT PID, SelectedUnit, Quantity FROM InvoiceDetails WHERE InvoiceID='{invoice_id}'")
            old_details = cur.fetchall()
            cur.execute("SELECT PID, Quantity, Unit1, Unit2, ConversionFactor FROM Product")
            products = {}
            for row in cur.fetchall():
                products[row[0]] = {
                    'quantity': float(row[1]),
                    'unit1': row[2],
                    'unit2': row[3],
                    'cf': float(row[4]) if row[4] else None
                }
            for pid, selected_unit, qty in old_details:
                qty = float(qty)
                prod = products.get(pid)
                if prod:
                    if selected_unit == prod['unit1']:
                        qty_in_unit1 = qty
                    elif selected_unit == prod['unit2'] and prod['cf']:
                        qty_in_unit1 = qty / prod['cf']
                    else:
                        qty_in_unit1 = qty
                    products[pid]['quantity'] += qty_in_unit1
                    cur.execute(f"UPDATE Product SET Quantity = Quantity + {qty_in_unit1} WHERE PID = '{pid}'")

            # Process new line items
            pids = request.form.getlist('pid[]')
            qtys = request.form.getlist('qty[]')
            prices = request.form.getlist('price[]')
            units = request.form.getlist('unit[]')
            line_discounts = request.form.getlist('discount[]')
            order_discount = float(request.form.get('order_discount', 0) or 0)

            if not pids or all(p == '' for p in pids):
                flash('Không có mục nào', 'error')
                cur.close()
                db.close()
                return redirect(url_for('invoice_update', invoice_id=invoice_id))

            subtotal = 0
            lines = []
            deductions = {}
            for i in range(len(pids)):
                if pids[i] == '':
                    continue
                pid = pids[i]
                qty = float(qtys[i])
                price = int(prices[i])
                selected_unit = units[i]
                line_disc_amt = float(line_discounts[i]) if i < len(line_discounts) and line_discounts[i] else 0

                if pid not in products:
                    flash(f'Không tìm thấy sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('invoice_update', invoice_id=invoice_id))

                prod = products[pid]
                if selected_unit == prod['unit1']:
                    qty_in_unit1 = qty
                elif selected_unit == prod['unit2'] and prod['cf']:
                    qty_in_unit1 = qty / prod['cf']
                else:
                    flash(f'Đơn vị không hợp lệ cho sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('invoice_update', invoice_id=invoice_id))

                deductions[pid] = deductions.get(pid, 0) + qty_in_unit1
                if deductions[pid] > products[pid]['quantity']:
                    flash(f'Số lượng tồn kho không đủ cho sản phẩm {pid}!', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('invoice_update', invoice_id=invoice_id))

                line_total = price * qty - line_disc_amt
                subtotal += line_total
                lines.append((pid, selected_unit, qty, price, qty_in_unit1, line_disc_amt))

            total_amt = subtotal - order_discount

            # Delete old details and insert new
            cur.execute(f"DELETE FROM InvoiceDetails WHERE InvoiceID='{invoice_id}'")
            cur.execute(f"UPDATE Invoices SET CID='{cid}', SalespersonID='{salesperson_id}', Discount={order_discount}, TotalAmt={total_amt} WHERE InvoiceID='{invoice_id}'")
            for pid, selected_unit, qty, price, qty_in_unit1, line_disc_amt in lines:
                cur.execute(f"INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES ('{invoice_id}', '{pid}', '{selected_unit}', {qty}, {price}, {line_disc_amt})")
                cur.execute(f"UPDATE Product SET Quantity = Quantity - {qty_in_unit1} WHERE PID = '{pid}'")
            db.commit()
            flash('Cập nhật hóa đơn thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('invoice_display', invoice_id=invoice_id))

    # GET: load invoice and details for editing
    cur.execute(f"SELECT * FROM Invoices WHERE InvoiceID='{invoice_id}'")
    invoice = cur.fetchone()
    if not invoice:
        flash('Không tìm thấy hóa đơn', 'error')
        cur.close()
        db.close()
        return redirect(url_for('invoice_display'))

    cid = invoice[1]
    salesperson_id = invoice[2] or ''
    cur.execute(f"SELECT CName FROM Customer WHERE CID='{cid}'")
    row = cur.fetchone()
    cname = row[0] if row else ''

    sname = ''
    if salesperson_id:
        cur.execute(f"SELECT SName FROM Salesperson WHERE SID='{salesperson_id}'")
        srow = cur.fetchone()
        sname = srow[0] if srow else ''

    cur.execute(f"SELECT InvoiceDetails.PID, Product.PName, InvoiceDetails.SelectedUnit, InvoiceDetails.Quantity, InvoiceDetails.Price, Product.Unit1, Product.Unit2, Product.ConversionFactor, Product.Price AS BasePrice, InvoiceDetails.Discount FROM InvoiceDetails JOIN Product ON InvoiceDetails.PID = Product.PID WHERE InvoiceDetails.InvoiceID='{invoice_id}'")
    items = cur.fetchall()
    order_discount = float(invoice[5] or 0)  # Invoices.Discount column

    cur.close()
    db.close()
    return render_template('invoices/update.html', invoice_id=invoice_id, cid=cid, cname=cname, salesperson_id=salesperson_id, sname=sname, items=items, order_discount=order_discount)


# --- Purchases ---

@app.route('/purchases/add', methods=['GET', 'POST'])
def purchase_add():
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            purchase_id = generate_purchase_id(cur)
            did = request.form['did']

            cur.execute("SELECT DID FROM Dealer")
            if (did,) not in cur.fetchall():
                flash("Nhà cung cấp không tồn tại", 'error')
                cur.close()
                db.close()
                return redirect(url_for('purchase_add'))

            pids = request.form.getlist('pid[]')
            qtys = request.form.getlist('qty[]')
            prices = request.form.getlist('price[]')
            units = request.form.getlist('unit[]')

            if not pids or all(p == '' for p in pids):
                flash('Không có mục nào', 'error')
                cur.close()
                db.close()
                return redirect(url_for('purchase_add'))

            # Load product info
            cur.execute("SELECT PID, Unit1, Unit2, ConversionFactor FROM Product")
            products = {}
            for row in cur.fetchall():
                products[row[0]] = {
                    'unit1': row[1],
                    'unit2': row[2],
                    'cf': float(row[3]) if row[3] else None
                }

            total_amt = 0
            lines = []
            for i in range(len(pids)):
                if pids[i] == '':
                    continue
                pid = pids[i]

                if pid not in products:
                    flash(f'Không tìm thấy sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('purchase_add'))

                prod = products[pid]
                qty = float(qtys[i])
                price = int(prices[i])
                selected_unit = units[i]

                # Convert to Unit1 for stock increment
                if selected_unit == prod['unit1']:
                    qty_in_unit1 = qty
                elif selected_unit == prod['unit2'] and prod['cf']:
                    qty_in_unit1 = qty / prod['cf']
                else:
                    flash(f'Đơn vị không hợp lệ cho sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('purchase_add'))

                total_amt += price * qty
                lines.append((pid, selected_unit, qty, price, qty_in_unit1))

            cur.execute(f"INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES ('{purchase_id}', '{did}', '{date.today()}', {total_amt})")
            for pid, selected_unit, qty, price, qty_in_unit1 in lines:
                cur.execute(f"INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES ('{purchase_id}', '{pid}', '{selected_unit}', {qty}, {price})")
                cur.execute(f"UPDATE Product SET Quantity = Quantity + {qty_in_unit1} WHERE PID = '{pid}'")
            db.commit()
            flash('Tạo phiếu nhập thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('purchase_add'))

    purchase_id = generate_purchase_id(cur)
    cur.close()
    db.close()
    return render_template('purchases/add.html', purchase_id=purchase_id)


@app.route('/purchases/delete', methods=['POST'])
def purchase_delete():
    db = get_db()
    cur = db.cursor()
    purchase_id = request.form.get('purchase_id')
    redirect_to = request.form.get('redirect_to', url_for('purchase_display'))
    cur.execute(f"SELECT PurchaseID FROM Purchases WHERE PurchaseID='{purchase_id}'")
    if not cur.fetchone():
        flash('Không tìm thấy phiếu nhập', 'error')
    else:
        # Restore stock before deleting (reverse the increments)
        cur.execute(f"SELECT PID, SelectedUnit, Quantity FROM PurchaseDetails WHERE PurchaseID='{purchase_id}'")
        details = cur.fetchall()
        cur.execute("SELECT PID, Unit1, Unit2, ConversionFactor FROM Product")
        prod_info = {}
        for row in cur.fetchall():
            prod_info[row[0]] = {'unit1': row[1], 'unit2': row[2], 'cf': float(row[3]) if row[3] else None}
        for pid, selected_unit, qty in details:
            qty = float(qty)
            prod = prod_info.get(pid)
            if prod:
                if selected_unit == prod['unit1']:
                    qty_in_unit1 = qty
                elif selected_unit == prod['unit2'] and prod['cf']:
                    qty_in_unit1 = qty / prod['cf']
                else:
                    qty_in_unit1 = qty
                cur.execute(f"UPDATE Product SET Quantity = Quantity - {qty_in_unit1} WHERE PID = '{pid}'")
        cur.execute(f"DELETE FROM Purchases WHERE PurchaseID='{purchase_id}'")
        db.commit()
        flash('Xóa phiếu nhập thành công', 'success')
    cur.close()
    db.close()
    return redirect(redirect_to)


@app.route('/purchases/update/<purchase_id>', methods=['GET', 'POST'])
def purchase_update(purchase_id):
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            did = request.form['did']
            cur.execute(f"SELECT DID FROM Dealer WHERE DID='{did}'")
            if not cur.fetchone():
                flash("Nhà cung cấp không tồn tại", 'error')
                cur.close()
                db.close()
                return redirect(url_for('purchase_update', purchase_id=purchase_id))

            # Restore old stock (reverse the increments)
            cur.execute(f"SELECT PID, SelectedUnit, Quantity FROM PurchaseDetails WHERE PurchaseID='{purchase_id}'")
            old_details = cur.fetchall()
            cur.execute("SELECT PID, Quantity, Unit1, Unit2, ConversionFactor FROM Product")
            products = {}
            for row in cur.fetchall():
                products[row[0]] = {
                    'quantity': float(row[1]),
                    'unit1': row[2],
                    'unit2': row[3],
                    'cf': float(row[4]) if row[4] else None
                }
            for pid, selected_unit, qty in old_details:
                qty = float(qty)
                prod = products.get(pid)
                if prod:
                    if selected_unit == prod['unit1']:
                        qty_in_unit1 = qty
                    elif selected_unit == prod['unit2'] and prod['cf']:
                        qty_in_unit1 = qty / prod['cf']
                    else:
                        qty_in_unit1 = qty
                    products[pid]['quantity'] -= qty_in_unit1
                    cur.execute(f"UPDATE Product SET Quantity = Quantity - {qty_in_unit1} WHERE PID = '{pid}'")

            # Process new line items
            pids = request.form.getlist('pid[]')
            qtys = request.form.getlist('qty[]')
            prices = request.form.getlist('price[]')
            units = request.form.getlist('unit[]')

            if not pids or all(p == '' for p in pids):
                flash('Không có mục nào', 'error')
                cur.close()
                db.close()
                return redirect(url_for('purchase_update', purchase_id=purchase_id))

            total_amt = 0
            lines = []
            for i in range(len(pids)):
                if pids[i] == '':
                    continue
                pid = pids[i]
                qty = float(qtys[i])
                price = int(prices[i])
                selected_unit = units[i]

                if pid not in products:
                    flash(f'Không tìm thấy sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('purchase_update', purchase_id=purchase_id))

                prod = products[pid]
                if selected_unit == prod['unit1']:
                    qty_in_unit1 = qty
                elif selected_unit == prod['unit2'] and prod['cf']:
                    qty_in_unit1 = qty / prod['cf']
                else:
                    flash(f'Đơn vị không hợp lệ cho sản phẩm {pid}', 'error')
                    cur.close()
                    db.close()
                    return redirect(url_for('purchase_update', purchase_id=purchase_id))

                total_amt += price * qty
                lines.append((pid, selected_unit, qty, price, qty_in_unit1))

            # Delete old details and insert new
            cur.execute(f"DELETE FROM PurchaseDetails WHERE PurchaseID='{purchase_id}'")
            cur.execute(f"UPDATE Purchases SET DID='{did}', TotalAmt={total_amt} WHERE PurchaseID='{purchase_id}'")
            for pid, selected_unit, qty, price, qty_in_unit1 in lines:
                cur.execute(f"INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES ('{purchase_id}', '{pid}', '{selected_unit}', {qty}, {price})")
                cur.execute(f"UPDATE Product SET Quantity = Quantity + {qty_in_unit1} WHERE PID = '{pid}'")
            db.commit()
            flash('Cập nhật phiếu nhập thành công', 'success')
        except Exception:
            flash('Dữ liệu không hợp lệ!', 'error')
        finally:
            cur.close()
            db.close()
        return redirect(url_for('purchase_display', purchase_id=purchase_id))

    # GET: load purchase and details for editing
    cur.execute(f"SELECT * FROM Purchases WHERE PurchaseID='{purchase_id}'")
    purchase = cur.fetchone()
    if not purchase:
        flash('Không tìm thấy phiếu nhập', 'error')
        cur.close()
        db.close()
        return redirect(url_for('purchase_display'))

    did = purchase[1]
    cur.execute(f"SELECT DName FROM Dealer WHERE DID='{did}'")
    row = cur.fetchone()
    dname = row[0] if row else ''

    cur.execute(f"SELECT PurchaseDetails.PID, Product.PName, PurchaseDetails.SelectedUnit, PurchaseDetails.Quantity, PurchaseDetails.Price, Product.Unit1, Product.Unit2, Product.ConversionFactor, Product.Price AS BasePrice FROM PurchaseDetails JOIN Product ON PurchaseDetails.PID = Product.PID WHERE PurchaseDetails.PurchaseID='{purchase_id}'")
    items = cur.fetchall()

    cur.close()
    db.close()
    return render_template('purchases/update.html', purchase_id=purchase_id, did=did, dname=dname, items=items)


@app.route('/purchases/display')
def purchase_display():
    purchase_id = request.args.get('purchase_id')
    if purchase_id:
        db = get_db()
        cur = db.cursor()
        cur.execute(f"SELECT * FROM Purchases WHERE PurchaseID='{purchase_id}'")
        purchase = cur.fetchone()
        dname = None
        items = []
        items_total = 0
        if not purchase:
            flash('Không tìm thấy phiếu nhập', 'error')
        else:
            cur.execute(f"SELECT DName FROM Dealer WHERE DID='{purchase[1]}'")
            row = cur.fetchone()
            dname = row[0] if row else '(đã xóa)'
            cur.execute(f"SELECT Product.PID, PName, PurchaseDetails.SelectedUnit, PurchaseDetails.Quantity, PurchaseDetails.Price FROM PurchaseDetails, Product WHERE PurchaseDetails.PurchaseID='{purchase_id}' AND PurchaseDetails.PID = Product.PID")
            items = cur.fetchall()
            items_total = sum(float(item[3]) * float(item[4]) for item in items)
        cur.close()
        db.close()
        return render_template('purchases/display.html', purchase_id=purchase_id, purchase=purchase, dname=dname, items=items, items_total=items_total)

    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cur = db.cursor()

    where_clauses = [f"(Purchases.PurchaseID LIKE '%{q}%' OR Purchases.DID LIKE '%{q}%')"]
    where_sql = " AND ".join(where_clauses)

    cur.execute(f"SELECT COUNT(*) FROM Purchases LEFT JOIN Dealer ON Purchases.DID = Dealer.DID WHERE {where_sql}")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT Purchases.PurchaseID, Purchases.DID, Dealer.DName, Purchases.PurchaseDate, Purchases.TotalAmt FROM Purchases LEFT JOIN Dealer ON Purchases.DID = Dealer.DID WHERE {where_sql} ORDER BY Purchases.PurchaseDate DESC, Purchases.PurchaseID DESC LIMIT {per_page} OFFSET {offset}")
    purchases = cur.fetchall()

    cur.close()
    db.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template('purchases/display.html', purchases=purchases, q=q, page=page, total_pages=total_pages)



# --- API ---

@app.route('/api/product/<pid>')
def api_product(pid):
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT PName, Unit1, Unit2, ConversionFactor, Price FROM Product WHERE PID='{pid}'")
    row = cur.fetchone()
    cur.close()
    db.close()
    if not row:
        return jsonify(error='Không tìm thấy sản phẩm'), 404
    result = {
        'pname': row[0],
        'unit1': row[1],
        'unit2': row[2],
        'conversion_factor': float(row[3]) if row[3] else None,
        'price': row[4]
    }
    return jsonify(result)


@app.route('/api/products')
def api_products():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT PID, PName, Unit1, Unit2, ConversionFactor, Quantity, Price FROM Product WHERE PName LIKE '%{q}%' LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return jsonify([{
        'pid': row[0],
        'pname': row[1],
        'unit1': row[2],
        'unit2': row[3],
        'conversion_factor': float(row[4]) if row[4] else None,
        'quantity': float(row[5]),
        'price': row[6]
    } for row in rows])


@app.route('/api/customers')
def api_customers():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT CID, CName, Address FROM Customer WHERE CName LIKE '%{q}%' LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return jsonify([{'cid': row[0], 'cname': row[1], 'address': row[2]} for row in rows])


@app.route('/api/dealers')
def api_dealers():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT DID, DName FROM Dealer WHERE DName LIKE '%{q}%' OR DID LIKE '%{q}%' LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return jsonify([{'did': row[0], 'dname': row[1]} for row in rows])


@app.route('/api/salespersons')
def api_salespersons():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    db = get_db()
    cur = db.cursor()
    cur.execute(f"SELECT SID, SName, Phone FROM Salesperson WHERE SName LIKE '%{q}%' OR SID LIKE '%{q}%' LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return jsonify([{'sid': row[0], 'sname': row[1], 'phone': row[2]} for row in rows])


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    init_db()
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.25, open_browser).start()
    app.run(host='127.0.0.1', port=5000)
