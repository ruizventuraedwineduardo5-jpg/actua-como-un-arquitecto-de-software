// Jarvis Dynamic Engine Client
const STORAGE_KEY = 'jarvis_app_records_' + window.location.pathname;

let records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

const itemInput = document.getElementById('itemTitle');
const addBtn = document.getElementById('addBtn');
const itemList = document.getElementById('itemList');
const counter = document.getElementById('counter');

function render() {
    itemList.innerHTML = '';
    records.forEach((rec, idx) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${rec.text} <small style="color: #64748b; margin-left: 8px;">${rec.time}</small></span>
            <button class="delete-btn" onclick="removeItem(${idx})">Eliminar</button>
        `;
        itemList.appendChild(li);
    });
    counter.textContent = records.length;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

function addItem() {
    const val = itemInput.value.trim();
    if (!val) return;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    records.push({ text: val, time: timeStr });
    itemInput.value = '';
    render();
}

function removeItem(idx) {
    records.splice(idx, 1);
    render();
}

addBtn.addEventListener('click', addItem);
itemInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addItem();
});

render();
