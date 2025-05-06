import os
from Bio import SeqIO
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    records = []
    try:
        if filename.lower().endswith(('.gb', '.gbk')):
            print(f"Parsing GenBank file: {filepath}")
            for record in SeqIO.parse(filepath, 'genbank'):
                features = [
                    {
                        'start': int(f.location.start),
                        'end': int(f.location.end),
                        'type': f.type,
                        'name': f.qualifiers.get('gene', [''])[0] or f.qualifiers.get('locus_tag', [''])[0],
                        'product': f.qualifiers.get('product', [''])[0]
                    }
                    for f in record.features if f.type in ['gene', 'CDS']
                ]
                records.append({
                    'metadata': {
                        'id': record.id,
                        'name': record.name,
                        'description': record.description,
                        'length': len(record.seq)
                    },
                    'features': features
                })

        elif filename.lower().endswith(('.fasta', '.fa', '.fna')):
            print(f"Parsing FASTA file: {filepath}")
            for record in SeqIO.parse(filepath, 'fasta'):
                seq = record.seq.upper()
                length = len(seq)
                gc_count = seq.count('G') + seq.count('C')
                at_count = seq.count('A') + seq.count('T')
                base_counts = {
                    'A': seq.count('A'),
                    'T': seq.count('T'),
                    'G': seq.count('G'),
                    'C': seq.count('C'),
                    'Other': length - (seq.count('A') + seq.count('T') + seq.count('G') + seq.count('C'))
                }
                records.append({
                    'metadata': {
                        'id': record.id,
                        'name': record.name,
                        'description': record.description,
                        'length': length,
                        'gc_content': round((gc_count / length) * 100, 2) if length else 0,
                        'at_content': round((at_count / length) * 100, 2) if length else 0,
                        'base_counts': base_counts,
                        'sample_sequence': str(seq[:100]) + ('...' if length > 100 else '')
                    },
                    'features': []  # No annotations in FASTA
            })


        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        if not records:
            return jsonify({'error': 'No records found in file.'}), 400

        return jsonify(records)

    except Exception as e:
        print(f"Error while parsing file: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
