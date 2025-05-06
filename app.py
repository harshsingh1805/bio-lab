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
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)

    filename = file.filename.lower()
    records = []

    try:
        if filename.endswith('.gb') or filename.endswith('.gbk'):
            print(f"Parsing GenBank file: {filepath}")
            for record in SeqIO.parse(filepath, 'genbank'):
                print(f"Record loaded: {record.id}")
                features = [
                    {
                        'start': int(f.location.start),
                        'end': int(f.location.end),
                        'type': f.type,
                        'name': f.qualifiers.get('gene', [''])[0],
                        'product': f.qualifiers.get('product', [''])[0]
                    }
                    for f in record.features if f.type in ['gene', 'CDS']
                ]
                print(f"Extracted {len(features)} gene/CDS features.")
                records.append({
                    'metadata': {
                        'id': record.id,
                        'name': record.name,
                        'description': record.description
                    },
                    'features': features
                })
        
        elif filename.endswith('.fasta') or filename.endswith('.fa'):
            print(f"Parsing FASTA file: {filepath}")
            for record in SeqIO.parse(filepath, 'fasta'):
                records.append({
                    'metadata': {
                        'id': record.id,
                        'name': record.name,
                        'description': record.description
                    },
                    'features': []  # No annotation
                })

        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        return jsonify(records)

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
