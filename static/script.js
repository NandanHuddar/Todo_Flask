
let authToken = localStorage.getItem('authToken');
let currentUserId = localStorage.getItem('userId');

const authSection = document.getElementById('authSection');
const userSection = document.getElementById('userSection');
const mainContent = document.getElementById('mainContent');
const usernameSpan = document.getElementById('username');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

if (authToken) {
    showMainContent();
    loadTasks();
} else {
    showAuthSection();
}

function showAuthSection() {
    authSection.classList.remove('hidden');
    userSection.classList.add('hidden');
    mainContent.classList.add('hidden');
}

function showMainContent() {
    authSection.classList.add('hidden');
    userSection.classList.remove('hidden');
    mainContent.classList.remove('hidden');
    usernameSpan.textContent = localStorage.getItem('username');
}

function showRegister() {
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
}

function showLogin() {
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    
    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            showLogin();
        } else {
            alert(data.message || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed');
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('username', username);
            
            showMainContent();
            loadTasks();
        } else {
            alert(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed');
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    authToken = null;
    showAuthSection();
}

async function addTask() {
    const name = document.getElementById('taskName').value;
    const description = document.getElementById('taskDescription').value;
    const dueDate = document.getElementById('taskDueDate').value;
    
    if (!name) {
        alert('Task name is required');
        return;
    }
    
    try {
        const response = await fetch('/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ name, description, due_date: dueDate })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('taskName').value = '';
            document.getElementById('taskDescription').value = '';
            document.getElementById('taskDueDate').value = '';
            loadTasks();
        } else {
            alert(data.message || 'Failed to add task');
        }
    } catch (error) {
        console.error('Add task error:', error);
        alert('Failed to add task');
    }
}

async function loadTasks() {
    try {
        const response = await fetch('/tasks', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayTasks(data.tasks);
        } else {
            alert(data.message || 'Failed to load tasks');
        }
    } catch (error) {
        console.error('Load tasks error:', error);
        alert('Failed to load tasks');
    }
}

function displayTasks(tasks) {
    const tasksList = document.getElementById('tasksList');
    tasksList.innerHTML = '';
    
    tasks.forEach(task => {
        const li = document.createElement('li');
        li.className = task.completed ? 'completed' : '';
        
        const dueDateStr = task.due_date ? new Date(task.due_date).toLocaleString() : '';
        
        li.innerHTML = `
            <div class="task-info">
                <h3>${task.name}</h3>
                <p>${task.description || ''}</p>
                ${dueDateStr ? `<div class="due-date">Due: ${dueDateStr}</div>` : ''}
            </div>
            <div class="task-actions">
                ${!task.completed ? `<button class="complete-btn" onclick="completeTask(${task.id})">Complete</button>` : ''}
                <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        `;
        
        tasksList.appendChild(li);
    });
}

async function completeTask(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/complete`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadTasks();
        } else {
            alert(data.message || 'Failed to complete task');
        }
    } catch (error) {
        console.error('Complete task error:', error);
        alert('Failed to complete task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadTasks();
        } else {
            alert(data.message || 'Failed to delete task');
        }
    } catch (error) {
        console.error('Delete task error:', error);
        alert('Failed to delete task');
    }
}
