// Set the current year in the footer dynamically
document.getElementById('year').textContent = new Date().getFullYear();

// Basic smooth scrolling for anchor links (if not supported by CSS natively in some older browsers)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Optional: Add a simple sticky navbar effect (changes background on scroll)
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        nav.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        nav.style.padding = '10px 0';
    } else {
        nav.style.padding = '15px 0';
    }
});

// Handle form submission via AJAX to prevent redirect
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default redirect
        
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerText;
        submitBtn.innerText = 'Sending...';
        submitBtn.disabled = true;

        const formData = new FormData(contactForm);
        
        // Use the AJAX endpoint for formsubmit.co
        fetch("https://formsubmit.co/ajax/info@sudhamoney.com", {
            method: "POST",
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success === "true" || data.success === true) {
                alert("Thank you! Your message has been sent successfully.");
                contactForm.reset();
            } else {
                alert("Oops! Something went wrong. Please try again.");
            }
        })
        .catch(error => {
            alert("Oops! There was a problem submitting your form.");
            console.error(error);
        })
        .finally(() => {
            submitBtn.innerText = originalBtnText;
            submitBtn.disabled = false;
        });
    });
}

