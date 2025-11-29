let currentConsultationId = null;

function showTab(tabName, event) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    buttons.forEach(btn => {
        const btnText = btn.textContent.toLowerCase();
        if ((tabName === 'consultation' && btnText.includes('consultation')) ||
            (tabName === 'history' && btnText.includes('history'))) {
            btn.classList.add('active');
        }
    });
    
    if (tabName === 'history') {
        loadHistory();
    }
}

document.getElementById('healthForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    submitBtn.disabled = true;
    loading.style.display = 'block';
    result.style.display = 'none';
    
    const formData = {
        symptoms: document.getElementById('symptoms').value,
        age: document.getElementById('age').value,
        medical_history: document.getElementById('medical_history').value
    };
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        loading.style.display = 'none';
        result.style.display = 'block';
        
        if (data.success) {
            result.classList.remove('error');
            resultContent.textContent = data.result;
            currentConsultationId = data.consultation_id;
            
            result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            result.classList.add('error');
            resultContent.textContent = 'Error: ' + data.error;
        }
    } catch (error) {
        loading.style.display = 'none';
        result.style.display = 'block';
        result.classList.add('error');
        resultContent.textContent = 'Error: ' + error.message;
    } finally {
        submitBtn.disabled = false;
    }
});

async function loadHistory() {
    const historyLoading = document.getElementById('history-loading');
    const historyList = document.getElementById('history-list');
    const noHistory = document.getElementById('no-history');
    
    historyLoading.style.display = 'block';
    historyList.innerHTML = '';
    noHistory.style.display = 'none';
    
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        historyLoading.style.display = 'none';
        
        if (data.success && data.history.length > 0) {
            data.history.reverse().forEach(item => {
                const card = createHistoryCard(item);
                historyList.appendChild(card);
            });
        } else {
            noHistory.style.display = 'block';
        }
    } catch (error) {
        historyLoading.style.display = 'none';
        historyList.innerHTML = `<p class="error">Error loading history: ${error.message}</p>`;
    }
}

function createHistoryCard(item) {
    const card = document.createElement('div');
    card.className = 'history-card';
    
    const date = new Date(item.timestamp);
    const formattedDate = date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    card.innerHTML = `
        <div class="history-header">
            <span class="history-date">📅 ${formattedDate}</span>
            <span class="history-age">Age: ${item.age}</span>
        </div>
        <div class="history-symptoms">${item.symptoms}</div>
        <div class="history-actions">
            <button onclick="viewConsultation(${item.id})" class="view-btn">View Full Report</button>
            <button onclick="exportConsultation(${item.id})" class="export-btn-small">Export</button>
        </div>
    `;
    
    return card;
}

async function viewConsultation(consultationId) {
    try {
        const response = await fetch(`/history/${consultationId}`);
        const data = await response.json();
        
        if (data.success) {
            showTab('consultation');
            
            const result = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            
            result.style.display = 'block';
            result.classList.remove('error');
            resultContent.textContent = data.consultation.result;
            currentConsultationId = consultationId;
            
            document.getElementById('symptoms').value = data.consultation.symptoms;
            document.getElementById('age').value = data.consultation.age;
            document.getElementById('medical_history').value = data.consultation.medical_history || '';
            
            setTimeout(() => {
                result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    } catch (error) {
        alert('Error loading consultation: ' + error.message);
    }
}

function exportResult() {
    if (currentConsultationId !== null) {
        exportConsultation(currentConsultationId);
    } else {
        const resultContent = document.getElementById('resultContent').textContent;
        downloadTextFile('health_assessment.txt', resultContent);
    }
}

function exportConsultation(consultationId) {
    window.location.href = `/export/${consultationId}`;
}

function downloadTextFile(filename, content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
