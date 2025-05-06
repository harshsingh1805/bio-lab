let allRecords = [];

let currentPage = 1;
const itemsPerPage = 100;

const form = document.getElementById('uploadForm');
const loading = document.getElementById('loading');

form.onsubmit = async function(e) {
    e.preventDefault();
    loading.style.display = 'block';

    const formData = new FormData(this);
    const res = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    loading.style.display = 'none';
    allRecords = await res.json();

    const selector = document.getElementById('recordSelector');
    selector.innerHTML = '<option disabled selected>Select a record</option>';

    allRecords.forEach((record, i) => {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${record.metadata.name} - ${record.metadata.description}`;
        selector.appendChild(option);
    });

    document.getElementById('plot').innerHTML = '';
    document.getElementById('details').textContent = '';
};

// Event listeners for both selectors
document.getElementById('recordSelector').onchange = renderSelectedRecord;
document.getElementById('featureFilter').onchange = renderSelectedRecord;

function renderSelectedRecord() {
    const index = document.getElementById('recordSelector').value;
    const filter = document.getElementById('featureFilter').value;
    if (!index) return;

    const data = allRecords[index];
    const filteredFeatures = data.features.filter(f => filter === 'all' || f.type === filter);

    const plotDiv = document.getElementById('plot');
    const detailsDiv = document.getElementById('details');

    // Always show metadata
    detailsDiv.textContent = JSON.stringify(data.metadata, null, 2);

    // ✅ Stop here if no features exist (FASTA file)
    if (filteredFeatures.length === 0) {
        plotDiv.innerHTML = '<div style="color: gray; font-style: italic;">No features to display for this record (FASTA files do not contain gene/CDS annotations).</div>';
        return; // ✅ Prevents plotting empty graph
    }

    const maxFeatures = 100;
    if (filteredFeatures.length > maxFeatures) {
        alert(`Showing only first ${maxFeatures} of ${filteredFeatures.length} features`);
    }

    const genes = filteredFeatures.slice(0, maxFeatures).map((f, i) => ({
        x: [f.start, f.end],
        y: [i, i],
        mode: 'lines',
        line: { width: 10 },
        name: f.name + ' (' + f.type + ')',
        hovertext: (f.product && f.product.trim()) || f.name || f.type || 'No info',
        hoverinfo: 'text'
    }));

    loading.style.display = 'block';

    Plotly.newPlot('plot', genes, {
        title: `Features: ${data.metadata.name}`,
        showlegend: true,
        margin: { t: 50 },
        hovermode: 'closest',
        xaxis: {
            title: 'Position on Genome',
            zeroline: false,
            showline: true
        },
        yaxis: {
            showticklabels: false
        }
    }, { responsive: true });

    document.getElementById('plot').on('plotly_click', function(plotData) {
        const point = plotData.points[0];
        const feature = genes[point.pointIndex];
        alert(`Feature: ${feature.name}\nFrom: ${feature.x[0]} to ${feature.x[1]}\nInfo: ${feature.hovertext}`);
    });

    loading.style.display = 'none';
}


document.getElementById('exportBtn').onclick = () => {
    const index = document.getElementById('recordSelector').value;
    if (!index) return alert("Select a record first.");
    const json = JSON.stringify(allRecords[index], null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'genome_metadata.json';
    a.click();
    URL.revokeObjectURL(url);
};
