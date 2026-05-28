// Global variables
let currentUser = null;
let currentSection = 'dashboard';
let apiBaseUrl = 'http://localhost:8000';

// DOM Elements
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('nav ul li a');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const taskForm = document.getElementById('task-form');
const projectForm = document.getElementById('project-form');
const wellnessForm = document.getElementById('wellness-form');

// Navigation
function showSection(sectionId) {
    // Hide all sections
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show the requested section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        currentSection = sectionId;
    }
    
    // Update active nav link
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });
    
    // Update login/register links visibility
    updateAuthLinks();
}

// Update auth links visibility based on login status
function updateAuthLinks() {
    const loginLink = document.getElementById('login-link');
    const registerLink = document.getElementById('register-link');
    
    if (currentUser) {
        loginLink.style.display = 'none';
        registerLink.style.display = 'none';
    } else {
        loginLink.style.display = 'block';
        registerLink.style.display = 'block';
    }
}

// API Functions
async function registerUser(userData) {
    try {
        const response = await fetch(`${apiBaseUrl}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful!');
            showSection('login');
            return data;
        } else {
            alert(`Registration failed: ${data.detail}`);
            return null;
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please try again.');
        return null;
    }
}

async function loginUser(credentials) {
    try {
        const response = await fetch(`${apiBaseUrl}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            localStorage.setItem('user', JSON.stringify(data));
            alert('Login successful!');
            showSection('dashboard');
            updateAuthLinks();
            loadDashboardData();
            return data;
        } else {
            alert(`Login failed: ${data.detail}`);
            return null;
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
        return null;
    }
}

// Load dashboard data
async function loadDashboardData() {
    if (!currentUser) return;
    
    try {
        // Load tasks
        const tasksResponse = await fetch(`${apiBaseUrl}/tasks`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const tasks = await tasksResponse.json();
        const completedTasks = tasks.filter(task => task.status === 'completed').length;
        document.getElementById('completed-tasks').textContent = completedTasks;
        
        // Load time tracking
        const timeEntriesResponse = await fetch(`${apiBaseUrl}/time-entries`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const timeEntries = await timeEntriesResponse.json();
        const totalHours = timeEntries.reduce((sum, entry) => sum + entry.hours, 0);
        document.getElementById('tracked-hours').textContent = totalHours.toFixed(1);
        
        // Load wellness
        const wellnessResponse = await fetch(`${apiBaseUrl}/wellness-entries`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const wellnessEntries = await wellnessResponse.json();
        if (wellnessEntries.length > 0) {
            const latestEntry = wellnessEntries[wellnessEntries.length - 1];
            const wellnessScore = Math.round((latestEntry.mood === 'happy' ? 100 : 
                                              latestEntry.mood === 'neutral' ? 75 : 
                                              latestEntry.mood === 'sad' ? 50 : 25) + 
                                             (latestEntry.sleep / 24 * 25) + 
                                             (10 - latestEntry.stress) * 5);
            document.getElementById('wellness-score').textContent = wellnessScore;
        } else {
            document.getElementById('wellness-score').textContent = 'N/A';
        }
        
        // Load charts
        loadCharts(tasks, timeEntries);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load charts
function loadCharts(tasks, timeEntries) {
    // Productivity chart
    const productivityCtx = document.getElementById('productivity-chart').getContext('2d');
    new Chart(productivityCtx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Productivity Score',
                data: [75, 80, 65, 90, 85, 70, 80],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Task distribution chart
    const taskCtx = document.getElementById('task-distribution-chart').getContext('2d');
    new Chart(taskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'In Progress', 'Pending'],
            datasets: [{
                data: [
                    tasks.filter(t => t.status === 'completed').length,
                    tasks.filter(t => t.status === 'in_progress').length,
                    tasks.filter(t => t.status === 'pending').length
                ],
                backgroundColor: ['#27ae60', '#f39c12', '#e74c3c']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Load tasks
async function loadTasks() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/tasks`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const tasks = await response.json();
        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item';
            taskElement.innerHTML = `
                <h4>${task.title}</h4>
                <p>${task.description}</p>
                <p><strong>Project:</strong> ${task.project_id || 'None'}</p>
                <p><strong>Priority:</strong> <span class="priority-${task.priority}">${task.priority}</span></p>
                <p><strong>Status:</strong> ${task.status}</p>
                <p><strong>Due Date:</strong> ${task.due_date || 'None'}</p>
            `;
            tasksList.appendChild(taskElement);
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// Load projects
async function loadProjects() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/projects`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const projects = await response.json();
        const projectsList = document.getElementById('projects-list');
        projectsList.innerHTML = '';
        
        projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.className = 'project-item';
            projectElement.innerHTML = `
                <h4>${project.name}</h4>
                <p>${project.description}</p>
                <p><strong>Created:</strong> ${new Date(project.created_at).toLocaleDateString()}</p>
            `;
            projectsList.appendChild(projectElement);
        });
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Load wellness entries
async function loadWellnessEntries() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${apiBaseUrl}/wellness-entries`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`
            }
        });
        
        const entries = await response.json();
        const wellnessList = document.getElementById('wellness-list');
        wellnessList.innerHTML = '';
        
        entries.forEach(entry => {
            const entryElement = document.createElement('div');
            entryElement.className = 'wellness-item';
            entryElement.innerHTML = `
                <h4>Wellness Entry</h4>
                <p><strong>Mood:</strong> ${entry.mood}</p>
                <p><strong>Sleep:</strong> ${entry.sleep} hours</p>
                <p><strong>Stress:</strong> ${entry.stress}/10</p>
                <p><strong>Note:</strong> ${entry.note || 'None'}</p>
                <p><strong>Date:</strong> ${new Date(entry.created_at).toLocaleDateString()}</p>
            `;
            wellnessList.appendChild(entryElement);
        });
    } catch (error) {
        console.error('Error loading wellness entries:', error);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
        });
    });
    
    // Login form
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        await loginUser({ email, password });
    });
    
    // Register form
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        
        await registerUser({ name, email, password });
    });
    
    // Task form
    document.getElementById('add-task-btn').addEventListener('click', function() {
        taskForm.classList.toggle('hidden');
    });
    
    document.getElementById('cancel-task').addEventListener('click', function() {
        taskForm.classList.add('hidden');
        document.getElementById('task-form-content').reset();
    });
    
    // Project form
    document.getElementById('add-project-btn').addEventListener('click', function() {
        projectForm.classList.toggle('hidden');
    });
    
    document.getElementById('cancel-project').addEventListener('click', function() {
        projectForm.classList.add('hidden');
        document.getElementById('project-form-content').reset();
    });
    
    // Wellness form
    document.getElementById('add-wellness-btn').addEventListener('click', function() {
        wellnessForm.classList.toggle('hidden');
    });
    
    document.getElementById('cancel-wellness').addEventListener('click', function() {
        wellnessForm.classList.add('hidden');
        document.getElementById('wellness-form-content').reset();
    });
    
    // Check for saved user
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateAuthLinks();
        showSection('dashboard');
        loadDashboardData();
    } else {
        showSection('login');
    }
});

// Initialize the app
showSection('login');