from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Donor, BloodStock, Request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bloodbank_secret_key'

db.init_app(app)

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

def init_stock():
    for bg in BLOOD_GROUPS:
        if not BloodStock.query.filter_by(blood_group=bg).first():
            db.session.add(BloodStock(blood_group=bg, units=0))
    db.session.commit()

# ─── HOME ────────────────────────────────────────────────────
@app.route('/')
def index():
    total_donors = Donor.query.count()
    total_requests = Request.query.count()
    pending_requests = Request.query.filter_by(status='Pending').count()
    stock = BloodStock.query.all()
    return render_template('index.html',
        total_donors=total_donors,
        total_requests=total_requests,
        pending_requests=pending_requests,
        stock=stock
    )

# ─── DONORS ──────────────────────────────────────────────────
@app.route('/donors')
def donors():
    search = request.args.get('search', '')
    bg_filter = request.args.get('blood_group', '')
    query = Donor.query
    if search:
        query = query.filter(Donor.name.ilike(f'%{search}%'))
    if bg_filter:
        query = query.filter_by(blood_group=bg_filter)
    all_donors = query.order_by(Donor.registered_on.desc()).all()
    return render_template('donors.html', donors=all_donors, blood_groups=BLOOD_GROUPS,
                           search=search, bg_filter=bg_filter)

@app.route('/add-donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        donor = Donor(
            name=request.form['name'],
            age=int(request.form['age']),
            blood_group=request.form['blood_group'],
            contact=request.form['contact'],
            email=request.form.get('email', ''),
            city=request.form.get('city', ''),
            last_donation=request.form.get('last_donation', '')
        )
        db.session.add(donor)
        # Update stock
        stock = BloodStock.query.filter_by(blood_group=donor.blood_group).first()
        if stock:
            stock.units += 1
        db.session.commit()
        flash(f'Donor {donor.name} registered successfully!', 'success')
        return redirect(url_for('donors'))
    return render_template('add_donor.html', blood_groups=BLOOD_GROUPS)

@app.route('/delete-donor/<int:id>')
def delete_donor(id):
    donor = Donor.query.get_or_404(id)
    stock = BloodStock.query.filter_by(blood_group=donor.blood_group).first()
    if stock and stock.units > 0:
        stock.units -= 1
    db.session.delete(donor)
    db.session.commit()
    flash('Donor removed.', 'info')
    return redirect(url_for('donors'))

# ─── BLOOD REQUESTS ──────────────────────────────────────────
@app.route('/requests')
def requests_page():
    all_requests = Request.query.order_by(Request.requested_on.desc()).all()
    return render_template('requests.html', requests=all_requests, blood_groups=BLOOD_GROUPS)

@app.route('/add-request', methods=['GET', 'POST'])
def add_request():
    if request.method == 'POST':
        req = Request(
            patient_name=request.form['patient_name'],
            blood_group=request.form['blood_group'],
            units_needed=int(request.form['units_needed']),
            hospital=request.form.get('hospital', ''),
            contact=request.form.get('contact', '')
        )
        db.session.add(req)
        db.session.commit()
        flash('Blood request submitted!', 'success')
        return redirect(url_for('requests_page'))
    return render_template('add_request.html', blood_groups=BLOOD_GROUPS)

@app.route('/update-request/<int:id>/<status>')
def update_request(id, status):
    req = Request.query.get_or_404(id)
    if status == 'Approved':
        stock = BloodStock.query.filter_by(blood_group=req.blood_group).first()
        if stock and stock.units >= req.units_needed:
            stock.units -= req.units_needed
            req.status = 'Approved'
            db.session.commit()
            flash('Request approved and stock updated.', 'success')
        else:
            flash('Not enough blood units in stock!', 'danger')
    elif status == 'Rejected':
        req.status = 'Rejected'
        db.session.commit()
        flash('Request rejected.', 'info')
    return redirect(url_for('requests_page'))

# ─── STOCK ───────────────────────────────────────────────────
@app.route('/stock')
def stock():
    all_stock = BloodStock.query.all()
    return render_template('stock.html', stock=all_stock)

@app.route('/update-stock', methods=['POST'])
def update_stock():
    blood_group = request.form['blood_group']
    units = int(request.form['units'])
    stock = BloodStock.query.filter_by(blood_group=blood_group).first()
    if stock:
        stock.units = units
        db.session.commit()
        flash(f'Stock for {blood_group} updated to {units} units.', 'success')
    return redirect(url_for('stock'))

# ─── SEARCH ──────────────────────────────────────────────────
@app.route('/search')
def search():
    bg = request.args.get('blood_group', '')
    donors_found = []
    stock_info = None
    if bg:
        donors_found = Donor.query.filter_by(blood_group=bg).all()
        stock_info = BloodStock.query.filter_by(blood_group=bg).first()
    return render_template('search.html', donors=donors_found, blood_groups=BLOOD_GROUPS,
                           selected_bg=bg, stock=stock_info)

# ─── RUN ─────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_stock()
    app.run(debug=True)
