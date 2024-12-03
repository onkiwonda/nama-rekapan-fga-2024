from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

app = Flask(__name__)

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pelatihan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Database
class Pelatihan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tanggal_mulai = db.Column(db.String(10), nullable=False)
    tanggal_selesai = db.Column(db.String(10), nullable=False)
    lokasi = db.Column(db.String(100), nullable=False)
    provinsi = db.Column(db.String(100), nullable=False)
    id_pelatihan = db.Column(db.String(50), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    nama_pelatihan = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(200), nullable=False)
    mitra = db.Column(db.String(100), nullable=False)
    pendaftar = db.Column(db.Integer, nullable=False)
    diterima = db.Column(db.Integer, nullable=False)
    onboarding = db.Column(db.Integer, nullable=False)
    menyelesaikan = db.Column(db.Integer, nullable=False)
    berhak_sertifikasi = db.Column(db.Integer, nullable=False)
    ikut_sertifikasi = db.Column(db.Integer, nullable=False)
    lulus_sertifikasi = db.Column(db.Integer, nullable=False)

# Inisialisasi database
with app.app_context():
    db.create_all()

# Global variable untuk target
target = 0

# Route untuk halaman utama
@app.route('/')
def index():
    data = Pelatihan.query.all()
    rekap = calculate_rekap(data)
    return render_template('index.html', data=data, rekap=rekap, target=target)

# Route untuk menambahkan data pelatihan
@app.route('/add', methods=['POST'])
def add_data():
    new_data = Pelatihan(
        tanggal_mulai=request.form["tanggal_mulai"],
        tanggal_selesai=request.form["tanggal_selesai"],
        lokasi=request.form["lokasi"],
        provinsi=request.form["provinsi"],
        id_pelatihan=request.form["id_pelatihan"],
        batch=request.form["batch"],
        nama_pelatihan=request.form["nama_pelatihan"],
        tema=request.form["tema"],
        mitra=request.form["mitra"],
        pendaftar=int(request.form["pendaftar"]),
        diterima=int(request.form["diterima"]),
        onboarding=int(request.form["onboarding"]),
        menyelesaikan=int(request.form["menyelesaikan"]),
        berhak_sertifikasi=int(request.form["berhak_sertifikasi"]),
        ikut_sertifikasi=int(request.form["ikut_sertifikasi"]),
        lulus_sertifikasi=int(request.form["lulus_sertifikasi"]),
    )
    db.session.add(new_data)
    db.session.commit()
    return redirect('/')

# Route untuk mengedit target
@app.route('/edit_target', methods=['GET', 'POST'])
def edit_target():
    global target
    if request.method == 'POST':
        target = int(request.form["target"])
        return redirect('/')
    return render_template('edit_target.html', target=target)

# Fungsi untuk menghitung rekapitulasi data
def calculate_rekap(data):
    if not data:
        return {key: 0 for key in ["Pendaftar", "Diterima", "Onboarding", "Menyelesaikan", "Berhak Sertifikasi", "Ikut Sertifikasi", "Lulus Sertifikasi"]}
    return {
        "Pendaftar": sum(d.pendaftar for d in data),
        "Diterima": sum(d.diterima for d in data),
        "Onboarding": sum(d.onboarding for d in data),
        "Menyelesaikan": sum(d.menyelesaikan for d in data),
        "Berhak Sertifikasi": sum(d.berhak_sertifikasi for d in data),
        "Ikut Sertifikasi": sum(d.ikut_sertifikasi for d in data),
        "Lulus Sertifikasi": sum(d.lulus_sertifikasi for d in data),
    }

@app.route('/rekap_provinsi', methods=['GET'])
def rekap_provinsi():
    rekap_data = db.session.query(
        Pelatihan.provinsi,
        db.func.sum(Pelatihan.pendaftar).label('total_pendaftar'),
        db.func.sum(Pelatihan.diterima).label('total_diterima'),
        db.func.sum(Pelatihan.onboarding).label('total_onboarding'),
        db.func.sum(Pelatihan.menyelesaikan).label('total_menyelesaikan'),
        db.func.sum(Pelatihan.berhak_sertifikasi).label('total_berhak_sertifikasi'),
        db.func.sum(Pelatihan.ikut_sertifikasi).label('total_ikut_sertifikasi'),
        db.func.sum(Pelatihan.lulus_sertifikasi).label('total_lulus_sertifikasi')
    ).group_by(Pelatihan.provinsi).all()

    # Format data dalam bentuk JSON
    result = {data[0]: {
        'pendaftar': data[1],
        'diterima': data[2],
        'onboarding': data[3],
        'menyelesaikan': data[4],
        'berhak_sertifikasi': data[5],
        'ikut_sertifikasi': data[6],
        'lulus_sertifikasi': data[7]
    } for data in rekap_data}

    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
