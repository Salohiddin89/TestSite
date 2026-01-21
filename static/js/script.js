// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Animation for slide out
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-20px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Test submission confirmation
function confirmSubmit() {
    const inputs = document.querySelectorAll('input[type="radio"]:checked');
    const totalQuestions = document.querySelectorAll('.question-card').length;

    if (inputs.length < totalQuestions) {
        return confirm(`Siz ${inputs.length} ta savolga javob berdingiz. ${totalQuestions - inputs.length} ta savol javobsiz qoldi. Testni yakunlamoqchimisiz?`);
    }

    return confirm('Testni yakunlamoqchimisiz? Barcha javoblaringiz saqlanadi.');
}

// Show retake confirmation modal
function showRetakeConfirm() {
    const modal = document.getElementById('retakeModal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Close retake modal
function closeRetakeModal() {
    const modal = document.getElementById('retakeModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('retakeModal');
    if (event.target === modal) {
        closeRetakeModal();
    }
});

// Load previous answers if available
if (typeof previousAnswers !== 'undefined' && typeof hasPrevious !== 'undefined') {
    if (hasPrevious) {
        document.addEventListener('DOMContentLoaded', function () {
            Object.keys(previousAnswers).forEach(questionId => {
                const answer = previousAnswers[questionId];
                if (answer.selected) {
                    const input = document.querySelector(`input[name="question_${questionId}"][value="${answer.selected}"]`);
                    if (input) {
                        input.checked = true;

                        // Add visual feedback
                        const answerOption = input.closest('.answer-option');
                        if (answer.is_correct) {
                            answerOption.style.background = '#d1fae5';
                            answerOption.style.borderColor = '#10b981';
                        } else {
                            answerOption.style.background = '#fee2e2';
                            answerOption.style.borderColor = '#ef4444';
                        }
                    }
                }
            });

            // Disable all inputs
            const allInputs = document.querySelectorAll('input[type="radio"]');
            allInputs.forEach(input => {
                input.disabled = true;
            });

            // Hide submit button
            const submitSection = document.querySelector('.submit-section');
            if (submitSection) {
                submitSection.style.display = 'none';
            }
        });
    }
}

// Smooth scroll to top on page load
window.addEventListener('load', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Add animation to cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function (entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.5s ease-out';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.question-card, .review-card');
    cards.forEach(card => {
        observer.observe(card);
    });
});

// Progress indicator for test taking
document.addEventListener('DOMContentLoaded', function () {
    const questionCards = document.querySelectorAll('.question-card');

    questionCards.forEach(card => {
        const inputs = card.querySelectorAll('input[type="radio"]');
        inputs.forEach(input => {
            input.addEventListener('change', function () {
                card.style.borderLeft = '4px solid #10b981';
                updateProgress();
            });
        });
    });
});

function updateProgress() {
    const totalQuestions = document.querySelectorAll('.question-card').length;
    const answeredQuestions = document.querySelectorAll('input[type="radio"]:checked').length;

    // You can add a progress bar here if needed
    console.log(`Progress: ${answeredQuestions}/${totalQuestions}`);
}

// Score circle animation
document.addEventListener('DOMContentLoaded', function () {
    const scoreCircle = document.querySelector('.score-fill');
    if (scoreCircle) {
        setTimeout(() => {
            const score = scoreCircle.getAttribute('data-score');
            const total = scoreCircle.getAttribute('data-total');
            const percentage = (score / total) * 283; // 283 is the circumference
            scoreCircle.style.strokeDasharray = `${percentage} 283`;
        }, 100);
    }
});

// Add hover effect to answer options
document.addEventListener('DOMContentLoaded', function () {
    const answerOptions = document.querySelectorAll('.answer-option');
    answerOptions.forEach(option => {
        option.addEventListener('mouseenter', function () {
            this.style.transform = 'translateX(5px)';
        });
        option.addEventListener('mouseleave', function () {
            this.style.transform = 'translateX(0)';
        });
    });
});