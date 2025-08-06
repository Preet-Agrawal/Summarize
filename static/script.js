let quizData = [];
let userAnswers = [];
let score = 0;
let quizCompleted = false;
let currentQuizId = null;

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menuToggle');
  const navMenu = document.getElementById('navMenu');
  
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', function() {
      menuToggle.classList.toggle('active');
      navMenu.classList.toggle('active');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!menuToggle.contains(event.target) && !navMenu.contains(event.target)) {
        menuToggle.classList.remove('active');
        navMenu.classList.remove('active');
      }
    });
    
    // Close menu when clicking on a link
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
          menuToggle.classList.remove('active');
          navMenu.classList.remove('active');
        }
      });
    });
  }
});

async function submitStory() {
  const inputText = document.getElementById("storyInput").value.trim();
  
  if (!inputText) {
    alert("Please enter a story first!");
    return;
  }

  // Show loading
  document.getElementById("loadingSection").style.display = "block";
  document.getElementById("resultSection").style.display = "none";

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || "Failed to generate quiz");
    }

    // Hide loading and show results
    document.getElementById("loadingSection").style.display = "none";
    document.getElementById("resultSection").style.display = "block";

    // Parse and display the result
    parseAndDisplayResult(data.result);
    
    // Store the quiz ID for later use
    if (data.quiz_id) {
      currentQuizId = data.quiz_id;
    }
    
    // Show success notification
    showSuccessNotification();
    
  } catch (error) {
    document.getElementById("loadingSection").style.display = "none";
    
    // Check if it's an authentication error (HTML response instead of JSON)
    if (error.message.includes("Unexpected token '<'") || 
        error.message.includes("JSON") || 
        error.message.includes("Failed to fetch")) {
      showLoginPopup();
    } else {
      alert("Error: " + error.message);
    }
  }
}

function parseAndDisplayResult(result) {
  const lines = result.split('\n');
  let currentSection = '';
  let summary = '';
  let questions = [];
  let currentQuestion = null;

  for (let line of lines) {
    line = line.trim();
    if (!line) continue;

    if (line.startsWith('SUMMARY:')) {
      currentSection = 'summary';
      continue;
    } else if (line.startsWith('QUIZ:')) {
      currentSection = 'quiz';
      continue;
    }

    if (currentSection === 'summary') {
      summary += line + '\n';
    } else if (currentSection === 'quiz') {
      // Parse quiz questions
      if (/^\d+\./.test(line)) {
        if (currentQuestion) {
          questions.push(currentQuestion);
        }
        currentQuestion = {
          question: line.replace(/^\d+\.\s*/, ''),
          options: [],
          correct: ''
        };
      } else if (line.match(/^[A-D]\)/)) {
        const option = line.replace(/^[A-D]\)\s*/, '');
        const optionLetter = line.charAt(0);
        currentQuestion.options.push({ letter: optionLetter, text: option });
      } else if (line.startsWith('Correct:')) {
        currentQuestion.correct = line.replace('Correct:', '').trim();
      }
    }
  }

  if (currentQuestion) {
    questions.push(currentQuestion);
  }

  // Store quiz data
  quizData = questions;
  userAnswers = new Array(questions.length).fill(null);
  score = 0;
  quizCompleted = false;

  // Display summary
  document.getElementById("summaryContent").innerHTML = summary.replace(/\n/g, '<br>');

  // Display quiz
  displayQuiz(questions);

  // Reset UI
  document.getElementById("scoreText").textContent = "Score: 0/5";
  document.getElementById("quizResults").style.display = "none";
}

function displayQuiz(questions) {
  const quizContent = document.getElementById("quizContent");
  quizContent.innerHTML = '';

  questions.forEach((q, index) => {
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question-container';
    questionDiv.innerHTML = `
      <h3 class="question-title">Question ${index + 1}</h3>
      <p class="question-text">${q.question}</p>
      <div class="options-container">
        ${q.options.map(option => `
          <button class="option-btn" 
                  data-question="${index}" 
                  data-option="${option.letter}"
                  onclick="selectOption(${index}, '${option.letter}')">
            <span class="option-letter">${option.letter})</span>
            <span class="option-text">${option.text}</span>
          </button>
        `).join('')}
      </div>
      <div class="feedback" id="feedback-${index}"></div>
    `;
    quizContent.appendChild(questionDiv);
  });
}

function selectOption(questionIndex, selectedOption) {
  if (quizCompleted) return;

  // Update user answer
  userAnswers[questionIndex] = selectedOption;

  // Check if correct
  const isCorrect = selectedOption === quizData[questionIndex].correct;
  
  // Update score - only increment if this is the first time answering correctly
  if (isCorrect) {
    score++;
  }

  // Update score display
  document.getElementById("scoreText").textContent = `Score: ${score}/5`;

  // Show feedback
  const feedbackDiv = document.getElementById(`feedback-${questionIndex}`);
  const optionBtns = document.querySelectorAll(`[data-question="${questionIndex}"]`);
  
  optionBtns.forEach(btn => {
    btn.disabled = true;
    btn.classList.remove('selected');
    const optionLetter = btn.getAttribute('data-option');
    
    if (optionLetter === quizData[questionIndex].correct) {
      btn.classList.add('correct');
    } else if (optionLetter === selectedOption && !isCorrect) {
      btn.classList.add('incorrect');
    }
    if (optionLetter === selectedOption) {
      btn.classList.add('selected'); // Add bounce animation
    }
  });

  if (isCorrect) {
    feedbackDiv.innerHTML = '<span class="correct-feedback">✅ Correct!</span>';
  } else {
    feedbackDiv.innerHTML = `<span class="incorrect-feedback">❌ Incorrect. The correct answer is ${quizData[questionIndex].correct})</span>`;
  }

  // Check if all questions are answered
  if (userAnswers.every(answer => answer !== null)) {
    showFinalResults();
  }
}

async function showFinalResults() {
  quizCompleted = true;
  const finalScoreDiv = document.getElementById("finalScore");
  const performanceDiv = document.getElementById("performanceMessage");
  
  finalScoreDiv.textContent = `Final Score: ${score}/5`;
  
  let performanceMessage = '';
  if (score === 5) {
    performanceMessage = "🎉 Perfect! You're a master of this story!";
    if (window.confetti) {
      confetti({
        particleCount: 120,
        spread: 90,
        origin: { y: 0.6 },
        zIndex: 9999
      });
    }
  } else if (score >= 4) {
    performanceMessage = "🌟 Excellent! You really understood the story well!";
  } else if (score >= 3) {
    performanceMessage = "👍 Good job! You have a solid understanding of the story.";
  } else if (score >= 2) {
    performanceMessage = "📚 Not bad! A bit more attention to detail would help.";
  } else {
    performanceMessage = "📖 Keep reading! Review the story and try again.";
  }
  
  performanceDiv.textContent = performanceMessage;
  document.getElementById("quizResults").style.display = "block";
  
  // Save the score to the database
  if (currentQuizId) {
    try {
      const response = await fetch("/save_score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          score: score, 
          quiz_id: currentQuizId 
        }),
      });
      
      if (!response.ok) {
        console.error("Failed to save score");
      }
    } catch (error) {
      console.error("Error saving score:", error);
    }
  }
}

function resetQuiz() {
  score = 0;
  userAnswers = new Array(quizData.length).fill(null);
  quizCompleted = false;
  
  document.getElementById("scoreText").textContent = "Score: 0/5";
  document.getElementById("quizResults").style.display = "none";
  
  // Reset all option buttons
  const optionBtns = document.querySelectorAll('.option-btn');
  optionBtns.forEach(btn => {
    btn.disabled = false;
    btn.classList.remove('correct', 'incorrect');
  });
  
  // Clear feedback
  const feedbacks = document.querySelectorAll('.feedback');
  feedbacks.forEach(feedback => {
    feedback.innerHTML = '';
  });
} 

function showLoginPopup() {
  const popup = document.createElement('div');
  popup.className = 'login-popup-overlay';
  popup.innerHTML = `
    <div class="login-popup">
      <div class="login-popup-header">
        <h3>🔐 Login Required</h3>
        <button class="close-popup" onclick="closeLoginPopup()">×</button>
      </div>
      <div class="login-popup-content">
        <p>You need to log in first to use the Summarize & Quiz feature!</p>
        <div class="login-popup-buttons">
          <button class="login-btn" onclick="goToLogin()">Login Now</button>
          <button class="register-btn" onclick="goToRegister()">Register</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(popup);
  
  // Add fade-in animation
  setTimeout(() => popup.classList.add('show'), 10);
  
  // Close popup when clicking outside
  popup.addEventListener('click', function(e) {
    if (e.target === popup) {
      closeLoginPopup();
    }
  });
  
  // Close popup with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeLoginPopup();
    }
  });
}

function closeLoginPopup() {
  const popup = document.querySelector('.login-popup-overlay');
  if (popup) {
    popup.classList.remove('show');
    setTimeout(() => popup.remove(), 300);
  }
}

function goToLogin() {
  window.location.href = '/login';
}

function goToRegister() {
  window.location.href = '/register';
} 

function showSuccessNotification() {
  const notification = document.createElement('div');
  notification.className = 'success-notification';
  notification.innerHTML = `
    <div class="success-content">
      <span class="success-icon">✅</span>
      <span class="success-text">Quiz generated successfully!</span>
    </div>
  `;
  document.body.appendChild(notification);
  
  // Show notification
  setTimeout(() => notification.classList.add('show'), 100);
  
  // Hide notification after 3 seconds
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
} 
