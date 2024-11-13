const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

// Initial canvas size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
let particleCount = calculateParticleCount();

// Class to represent individual particles
class Particle {
    constructor() {
        this.reset();
        // Random starting position
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;

        // Red hues
        this.colors = ['#FF0000', '#FF6347', '#FF4500', '#D32F2F', '#B71C1C']; // Red hues
        this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.speed = Math.random() / 5 + 0.05; // Slow speed
        this.opacity = Math.random() * 0.3 + 0.5; // Subtle opacity
        this.size = 2; // Small 2px size for each particle
        this.fadeDelay = Math.random() * 600 + 100;
        this.fadeStart = Date.now() + this.fadeDelay;
        this.fadingOut = false;
    }

    update() {
        this.y -= this.speed; // Move particles upward slowly

        if (this.y < 0) {
            this.reset(); // Reset particle when it moves off the screen
        }

        if (!this.fadingOut && Date.now() > this.fadeStart) {
            this.fadingOut = true; // Start fading the particle after a delay
        }

        if (this.fadingOut) {
            this.opacity -= 0.005; // Slow down the fade effect
            if (this.opacity <= 0) {
                this.reset(); // Reset when fully faded
            }
        }
    }

    draw() {
        // Set global alpha to handle opacity
        ctx.globalAlpha = this.opacity;

        // Draw the particle as a small 2px dot
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color; // Use the assigned random red color
        ctx.fill();

        ctx.globalAlpha = 1; // Reset alpha to 1 after drawing the particle
    }

    static drawLines(particles) {
        const maxDistance = 150; // Distance at which particles will be connected by lines
        ctx.lineWidth = 0.5; // Thin lines for a subtle effect

        // Draw lines between close particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                // Only draw lines if the particles are close enough
                if (distance < maxDistance) {
                    // Semi-transparent red line
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    
                    ctx.strokeStyle = 'rgba(255, 200, 200, 0.4)' // Subtle red lines
                    ctx.stroke();
                }
            }
        }
    }
}

function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw lines between particles that are close enough
    Particle.drawLines(particles);

    // Update and draw each particle
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    requestAnimationFrame(animate);
}

function calculateParticleCount() {
    // Reduce the particle count for better performance and a cleaner effect
    // Using a more reasonable divisor for particle density
    return Math.floor((canvas.width * canvas.height) / 15000); // Lower density of particles
}

function onResize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    particleCount = calculateParticleCount();
    initParticles();
}

window.addEventListener('resize', onResize);

// Initialize particles and start animation
initParticles();
animate();

// Navbar height handling (optional)
const navbar = document.querySelector('.navbar');
const navbarHeight = navbar.offsetHeight;
document.documentElement.style.setProperty('--navbar-height', `${navbarHeight}px`);
