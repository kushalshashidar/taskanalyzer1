const API_URL = 'http://localhost:8000/api/tasks';
let tasks = [];

// Tab Switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Form Handling
document.getElementById('task-form').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const title = document.getElementById('title').value;
    const dueDate = document.getElementById('due_date').value;
    const hours = parseFloat(document.getElementById('estimated_hours').value);
    const importance = parseInt(document.getElementById('importance').value);
    const depsInput = document.getElementById('dependencies').value;
    
    const dependencies = depsInput ? depsInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id)) : [];
    
    // Generate a temporary ID for local reference if not provided
    const id = tasks.length + 1; 
    
    const task = {
        id,
        title,
        due_date: dueDate,
        estimated_hours: hours,
        importance,
        dependencies
    };
    
    tasks.push(task);
    updatePreview();
    e.target.reset();
    document.getElementById('imp-val').textContent = '5';
});

function loadJson() {
    const input = document.getElementById('json-input').value;
    try {
        const jsonTasks = JSON.parse(input);
        if (Array.isArray(jsonTasks)) {
            tasks = [...tasks, ...jsonTasks];
            updatePreview();
            document.getElementById('json-input').value = '';
            alert(`Loaded ${jsonTasks.length} tasks`);
        } else {
            alert('Input must be an array of task objects');
        }
    } catch (e) {
        alert('Invalid JSON');
    }
}

function updatePreview() {
    const list = document.getElementById('task-list-preview');
    const count = document.getElementById('task-count');
    
    list.innerHTML = tasks.map(t => `
        <li class="preview-item">
            <span>#${t.id} ${t.title}</span>
            <span>${t.due_date}</span>
        </li>
    `).join('');
    
    count.textContent = tasks.length;
}

function clearList() {
    tasks = [];
    updatePreview();
    document.getElementById('results-container').innerHTML = '<div class="empty-state"><p>List cleared</p></div>';
}

async function analyzeTasks() {
    if (tasks.length === 0) {
        alert('Add tasks first!');
        return;
    }
    
    const strategy = document.getElementById('strategy').value;
    const container = document.getElementById('results-container');
    container.innerHTML = '<p style="text-align:center; color:var(--text-secondary)">Analyzing...</p>';
    
    try {
        // We send the strategy as a query param or in body. 
        // Let's send in body for simplicity since we are POSTing data anyway.
        // But wait, the serializer expects a list. 
        // We can wrap it: { tasks: [], strategy: '' } or just send list and use query param.
        // Let's use query param for strategy.
        
        const response = await fetch(`${API_URL}/analyze/?strategy=${strategy}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tasks)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(JSON.stringify(err));
        }
        
        const analyzedTasks = await response.json();
        renderResults(analyzedTasks);
        
    } catch (error) {
        container.innerHTML = `<div class="empty-state" style="color:var(--danger)"><p>Error: ${error.message}</p></div>`;
    }
}

function renderResults(analyzedTasks) {
    const container = document.getElementById('results-container');
    
    if (analyzedTasks.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No results</p></div>';
        return;
    }
    
    container.innerHTML = analyzedTasks.map(task => {
        let priorityClass = 'priority-low';
        if (task.score > 80) priorityClass = 'priority-high';
        else if (task.score > 50) priorityClass = 'priority-medium';
        
        return `
        <div class="task-card ${priorityClass}">
            <div class="task-header">
                <span class="task-title">#${task.id || '?'} ${task.title}</span>
                <span class="score-badge">${task.score}</span>
            </div>
            <div class="task-meta">
                <span>📅 ${task.due_date}</span>
                <span>⏱ ${task.estimated_hours}h</span>
                <span>⭐ ${task.importance}/10</span>
            </div>
            <div class="explanation">
                <strong>Why:</strong>
                <ul>
                    ${task.explanation.map(e => `<li>${e}</li>`).join('')}
                </ul>
            </div>
        </div>
        `;
    }).join('');
}
