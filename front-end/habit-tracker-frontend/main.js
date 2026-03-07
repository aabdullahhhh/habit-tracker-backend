import './style.css'
import { initScene, disposeScene } from './scene.js'

// State
let currentUser = null;
let habits = [];
let editingHabitId = null;

// DOM Elements
const views = {
  login: document.getElementById('login-view'),
  register: document.getElementById('register-view'),
  dashboard: document.getElementById('dashboard-view')
};

const modal = {
  overlay: document.getElementById('habit-modal'),
  title: document.getElementById('modal-title'),
  nameInput: document.getElementById('modal-habit-name'),
  descInput: document.getElementById('modal-habit-description'),
  freqSelect: document.getElementById('modal-habit-frequency'),
  btnSave: document.getElementById('btn-modal-save'),
  btnCancel: document.getElementById('btn-modal-cancel')
};

// Utilities
const generateId = () => Math.random().toString(36).substring(2, 9);
const saveState = () => {
  if (currentUser) {
    localStorage.setItem(`habits_${currentUser.username}`, JSON.stringify(habits));
  }
};
const loadState = () => {
  if (currentUser) {
    const saved = localStorage.getItem(`habits_${currentUser.username}`);
    habits = saved ? JSON.parse(saved) : [];
  }
};

// Routing
const showView = (viewName) => {
  Object.values(views).forEach(v => v.classList.add('hidden'));
  views[viewName].classList.remove('hidden');
  
  // Handle 3D Scene mounting
  // Removed initScene/disposeScene calls for login/register views as per instruction.
  // The 3D scene is now only initialized for the dashboard view.
  if (viewName === 'dashboard') {
    initScene('canvas-container-dashboard'); // Assuming a dashboard canvas exists
  } else {
    disposeScene();
  }
};

// Auth Mock Methods
const login = (email) => {
  // Simple mock login using email prefix as username
  const username = email.split('@')[0];
  currentUser = { email, username };
  loadState();
  initDashboard();
  showView('dashboard');
};
const register = (username, email) => {
  currentUser = { email, username };
  habits = [];
  saveState();
  initDashboard();
  showView('dashboard');
};
const logout = () => {
  currentUser = null;
  habits = [];
  document.getElementById('login-email').value = '';
  document.getElementById('login-password').value = '';
  showView('login');
};

// Dashboard
const initDashboard = () => {
  document.getElementById('nav-username').textContent = currentUser.username;
  document.getElementById('welcome-text').textContent = `Good evening, ${currentUser.username.charAt(0).toUpperCase() + currentUser.username.slice(1)}`;
  renderHabits();
};

const renderHabits = () => {
  const list = document.getElementById('habit-list');
  const count = document.getElementById('habit-count');
  
  const activeCount = habits.filter(h => h.active).length;
  count.textContent = `${activeCount} ACTIVE HABIT${activeCount !== 1 ? 'S' : ''}`;
  
  list.innerHTML = '';
  
  habits.forEach(habit => {
    const card = document.createElement('div');
    card.className = 'habit-card';
    card.innerHTML = `
      <div class="habit-details">
        <div class="body-16">${escapeHtml(habit.name)}</div>
        <div class="body-13">${escapeHtml(habit.description)}</div>
      </div>
      <div class="habit-badge-container">
        <div class="habit-badge">${habit.frequency}</div>
      </div>
      <div class="habit-actions">
        <!-- Toggle -->
        <div class="toggle ${habit.active ? 'active' : ''}" data-id="${habit.id}" role="switch"></div>
        <!-- Edit -->
        <button class="icon-btn edit" data-id="${habit.id}">
          <svg width="16" height="16"><use href="#icon-edit"></use></svg>
        </button>
        <!-- Delete -->
        <button class="icon-btn delete" data-id="${habit.id}">
          <svg width="16" height="16"><use href="#icon-trash"></use></svg>
        </button>
      </div>
    `;
    list.appendChild(card);
  });
};

const escapeHtml = (unsafe) => {
  return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
};

// Modal Handling
const openModal = (habitId = null) => {
  editingHabitId = habitId;
  
  if (habitId) {
    const habit = habits.find(h => h.id === habitId);
    modal.title.textContent = 'EDIT HABIT';
    modal.nameInput.value = habit.name;
    modal.descInput.value = habit.description;
    modal.freqSelect.value = habit.frequency;
  } else {
    modal.title.textContent = 'ADD HABIT';
    modal.nameInput.value = '';
    modal.descInput.value = '';
    modal.freqSelect.value = 'DAILY';
  }
  
  modal.overlay.classList.add('open');
};

const closeModal = () => {
  modal.overlay.classList.remove('open');
  editingHabitId = null;
};

const saveHabit = () => {
  const name = modal.nameInput.value.trim();
  const description = modal.descInput.value.trim();
  const frequency = modal.freqSelect.value;
  
  if (!name) return alert('Habit name is required');
  
  if (editingHabitId) {
    const habit = habits.find(h => h.id === editingHabitId);
    habit.name = name;
    habit.description = description;
    habit.frequency = frequency;
  } else {
    habits.push({
      id: generateId(),
      name,
      description,
      frequency,
      active: true,
      createdAt: Date.now()
    });
  }
  
  saveState();
  renderHabits();
  closeModal();
};

const deleteHabit = (id) => {
  if (confirm('Delete this habit?')) {
    habits = habits.filter(h => h.id !== id);
    saveState();
    renderHabits();
  }
};

const toggleHabitActive = (id) => {
  const habit = habits.find(h => h.id === id);
  if (habit) {
    habit.active = !habit.active;
    saveState();
    renderHabits();
  }
};


// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  
  // Quote Rotation Logic for Auth Views (Dark Forest)
let quoteInterval;
let quoteTimeout;
const initQuoteRotation = () => {
  const container = document.querySelector('#login-view .forest-quotes-container');
  if (!container) return;
  
  const quotesData = [
    "Every habit you keep is a step closer to the person you are becoming.",
    "The forest does not rush, yet everything is accomplished.",
    "Small actions, repeated daily, build extraordinary lives.",
    "Stillness is where clarity lives. Habits are where growth lives.",
    "Your future self is being built right now, one choice at a time."
  ];
  
  // Inject HTML
  container.innerHTML = '';
  const slides = quotesData.map((text, i) => {
    const slide = document.createElement('div');
    slide.className = 'forest-quote-slide' + (i === 0 ? ' active' : '');
    slide.innerHTML = `
      <p class="quote-playfair">"${text}"</p>
      <div class="quote-line"></div>
      <p class="quote-author">HABITFLOW JOURNAL</p>
    `;
    container.appendChild(slide);
    return slide;
  });
  
  let currentSlide = 0;
  clearInterval(quoteInterval);
  clearTimeout(quoteTimeout);
  
  // Cycle every 4 seconds
  quoteInterval = setInterval(() => {
    // 1. Fade old out (CSS handles 0.8s transition)
    slides[currentSlide].classList.remove('active');
    
    // 2. Wait 0.8s (fade out) + 0.3s (pause) = 1.1s before fading new one in
    quoteTimeout = setTimeout(() => {
      currentSlide = (currentSlide + 1) % slides.length;
      slides[currentSlide].classList.add('active');
    }, 1100);
    
  }, 4000); 
};
  initQuoteRotation();
  
  // Auth Flows
  document.getElementById('btn-login').addEventListener('click', () => {
    const email = document.getElementById('login-email').value;
    if (email) login(email);
  });
  
  document.getElementById('btn-register').addEventListener('click', () => {
    const user = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    if (user && email) register(user, email);
  });
  
  document.getElementById('link-go-register').addEventListener('click', (e) => {
    e.preventDefault();
    showView('register');
  });
  
  document.getElementById('link-go-login').addEventListener('click', (e) => {
    e.preventDefault();
    showView('login');
  });
  
  document.getElementById('btn-logout').addEventListener('click', logout);
  
  // Dashboard & Modal
  document.getElementById('btn-open-add-modal').addEventListener('click', () => openModal());
  modal.btnCancel.addEventListener('click', closeModal);
  modal.btnSave.addEventListener('click', saveHabit);
  
  // List Delegated Events
  document.getElementById('habit-list').addEventListener('click', (e) => {
    const toggle = e.target.closest('.toggle');
    const editBtn = e.target.closest('.icon-btn.edit');
    const deleteBtn = e.target.closest('.icon-btn.delete');
    
    if (toggle) toggleHabitActive(toggle.dataset.id);
    if (editBtn) openModal(editBtn.dataset.id);
    if (deleteBtn) deleteHabit(deleteBtn.dataset.id);
  });
  
  // Init
  showView('login');
});
