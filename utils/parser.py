from Bio import SeqIO

def parse_genbank(filepath):
    print(f"Parsing GenBank file: {filepath}")

    records = []
    with open(filepath, 'r') as handle:
        for i, record in enumerate(SeqIO.parse(handle, 'genbank')):
            if i >= 10:
                break  # Limit to first 10 records
            print("Record loaded:", record.id)

            metadata = {
                'id': record.id,
                'name': record.name,
                'description': record.description,
                'length': len(record.seq)
            }

            print("Extracting features...")
            features = []
            for feature in record.features:
                if feature.type in ['gene', 'CDS']:
                    features.append({
                        'start': int(feature.location.start),
                        'end': int(feature.location.end),
                        'strand': feature.location.strand,
                        'type': feature.type,
                        'name': feature.qualifiers.get('gene', [''])[0],
                        'product': feature.qualifiers.get('product', [''])[0]
                    })

            print(f"Extracted {len(features)} gene/CDS features.")
            records.append({
                'metadata': metadata,
                'features': features[:100]  # Limit features to first 100
            })

    if not records:
        raise ValueError("No valid GenBank record found.")

    return records

def parse_fasta(filepath):
    print(f"Parsing FASTA file: {filepath}")
    records = []
    with open(filepath, 'r') as handle:
        for i, record in enumerate(SeqIO.parse(handle, 'fasta')):
            if i >= 10:
                break
            metadata = {
                'id': record.id,
                'name': record.name,
                'description': record.description,
                'length': len(record.seq)
            }
            features = [{
                'start': 0,
                'end': len(record.seq),
                'type': 'sequence',
                'name': record.name,
                'product': 'FASTA sequence'
            }]
            records.append({'metadata': metadata, 'features': features})
    return records    
