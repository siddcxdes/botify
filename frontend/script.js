// Backend base URL (Render)
// Backend base URL
// - In production (Vercel), requests go to "/api" and are rewritten to Render via vercel.json
// - In local dev, use the FastAPI server on localhost:8000
const API_URL = (() => {
    const origin = window.location.origin;
    if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
        return 'http://localhost:8000';
    }
    return '/api';
})();

/* ============ AUTO-DEMO SCRIPTS ============ */
const autoScripts = {
    lawfirm: {
        greeting: "Hi! I'm the AI assistant for Smith & Associates. How can I help you today?",
        exchanges: [
            {
                user: "Do you handle divorce cases?",
                bot: "Yes, we specialize in family law including divorce, custody, and settlements. Would you like to schedule a free consultation?"
            },
            {
                user: "Yes, I'd like that",
                bot: "Great! Could I get your name, email, and phone number so our team can reach out within 24 hours?"
            },
            {
                user: "John, john@email.com, 555-1234",
                bot: "Thank you, John! A lawyer from our family law team will contact you shortly. Is there anything else I can help with?"
            }
        ]
    },
    realestate: {
        greeting: "Hello! I'm the AI assistant for GreenNest Realty. Looking to buy, sell, or rent?",
        exchanges: [
            {
                user: "I'm looking for a 3BHK under 80 lakhs",
                bot: "We have 6 options in your range across east and west zones — most with covered parking and society amenities. Want me to send you the listings?"
            },
            {
                user: "Yes please!",
                bot: "Perfect! Can I get your name and email? I'll send the brochure with photos and pricing right away."
            },
            {
                user: "Priya, priya@email.com",
                bot: "Thanks Priya! You'll receive the listings within 10 minutes. Our agent may also call to help schedule visits. Anything else?"
            }
        ]
    },
    dental: {
        greeting: "Hi there! I'm the AI assistant for BrightSmile Dental. How can I help?",
        exchanges: [
            {
                user: "How much does teeth whitening cost?",
                bot: "Our professional LED whitening starts at just Rs 2,500 per session — results visible in one sitting! Want to book an appointment?"
            },
            {
                user: "Sure, let's book it",
                bot: "Wonderful! Can I get your name, phone number, and preferred date? I'll confirm your slot right away."
            },
            {
                user: "Rahul, 9876543210, this Saturday",
                bot: "You're all set, Rahul! Saturday at BrightSmile Dental. We'll send a confirmation to your number. See you soon!"
            }
        ]
    }
};

/* ============ STATE ============ */
const state = {
    lawfirm:    { history: [], demoPlayed: false, demoRunning: false },
    realestate: { history: [], demoPlayed: false, demoRunning: false },
    dental:     { history: [], demoPlayed: false, demoRunning: false },
};

let activeDomain = null;

/* ============ HELPERS ============ */
function typeWriter(el, text, speed = 18) {
    return new Promise(resolve => {
        let i = 0; el.textContent = '';
        const box = el.closest('.chat-messages');
        (function type() {
            if (i < text.length) {
                el.textContent += text.charAt(i); i++;
                if (box) box.scrollTop = box.scrollHeight;
                setTimeout(type, speed);
            } else resolve();
        })();
    });
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

function addBubble(domain, role, text, typeEffect = false) {
    const container = document.getElementById(`messages-${domain}`);
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', role);
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
    if (typeEffect) return typeWriter(bubble, text);
    bubble.textContent = text;
    container.scrollTop = container.scrollHeight;
    return Promise.resolve();
}

function showTypingIndicator(domain) {
    const container = document.getElementById(`messages-${domain}`);
    const ind = document.createElement('div');
    ind.classList.add('typing-indicator'); ind.id = `typing-${domain}`;
    ind.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    container.appendChild(ind);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator(domain) {
    const el = document.getElementById(`typing-${domain}`);
    if (el) el.remove();
}

function enableInput(domain) {
    document.getElementById(`input-${domain}`).disabled = false;
    document.getElementById(`send-${domain}`).disabled = false;
    document.getElementById(`input-${domain}`).focus();
}

/* ============ AUTO DEMO ============ */
async function runAutoDemo(domain) {
    if (state[domain].demoPlayed || state[domain].demoRunning) return;
    state[domain].demoRunning = true;
    const script = autoScripts[domain];

    await delay(600);
    showTypingIndicator(domain);
    await delay(1200);
    removeTypingIndicator(domain);
    await addBubble(domain, 'bot', script.greeting, true);

    for (const ex of script.exchanges) {
        await delay(1500);
        await addBubble(domain, 'user', ex.user, true);
        await delay(800);
        showTypingIndicator(domain);
        await delay(1800);
        removeTypingIndicator(domain);
        await addBubble(domain, 'bot', ex.bot, true);
    }

    state[domain].demoPlayed = true;
    state[domain].demoRunning = false;
    await delay(500);
    enableInput(domain);
}

/* ============ DEMO OPEN / CLOSE ============ */
function openDemo(domain) {
    activeDomain = domain;
    document.querySelectorAll('.demo-inner').forEach(d => d.classList.remove('visible'));
    document.getElementById(`demo-${domain}`).classList.add('visible');
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
    if (!state[domain].demoPlayed && !state[domain].demoRunning) {
        runAutoDemo(domain);
    }
}

function closeDemo() {
    document.querySelectorAll('.demo-inner').forEach(d => d.classList.remove('visible'));
    document.getElementById('hero').scrollIntoView({ behavior: 'smooth' });
    activeDomain = null;
}

/* ============ SEND MESSAGE (API) ============ */
async function sendMessage(domain) {
    const input = document.getElementById(`input-${domain}`);
    const message = input.value.trim();
    if (!message) return;

    input.value = ''; input.disabled = true;
    document.getElementById(`send-${domain}`).disabled = true;

    addBubble(domain, 'user', message);
    state[domain].history.push({ role: 'user', content: message });

    await delay(300);
    showTypingIndicator(domain);

    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain, message, history: state[domain].history })
        });
        const data = await res.json();
        removeTypingIndicator(domain);
        if (data.reply) {
            await addBubble(domain, 'bot', data.reply, true);
            state[domain].history.push({ role: 'assistant', content: data.reply });
        } else {
            await addBubble(domain, 'bot', 'Sorry, something went wrong. Please try again.', true);
        }
    } catch (err) {
        removeTypingIndicator(domain);
        await addBubble(domain, 'bot', 'Could not reach the server. Make sure the backend is running at localhost:8000.', true);
    }
    enableInput(domain);
}

/* ============ ENTER KEY HANDLERS ============ */
['lawfirm', 'realestate', 'dental'].forEach(domain => {
    const inp = document.getElementById(`input-${domain}`);
    if (inp) inp.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(domain); }
    });
});

/* ============ SCROLL REVEAL ============ */
const revealObs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* ============ NAVBAR SCROLL ============ */
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (window.scrollY > 60) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

/* ============ AUTO-OPEN LAW FIRM DEMO ============ */
activeDomain = 'lawfirm';
runAutoDemo('lawfirm');

/* ============ POPUP FAB ENTRANCE (3s delay) ============ */
setTimeout(() => {
    document.getElementById('popupFab').classList.add('entered');
}, 3000);

/* ============ POPUP CHATBOT ============ */
let popupOpen = false;
let popupGreeted = false;

const popupReplies = [
    "A bot like me can sit on your website and answer customer questions 24/7.",
    "I get trained on YOUR content — services, pricing, FAQs, everything.",
    "When a visitor is interested, I capture their name, email, and phone for you.",
    "Setup takes under 5 minutes. Works with any website — Wordpress, Wix, Shopify, custom.",
    "Send your website link and I'll create a free demo — no commitment needed.",
    "Scroll down and click 'Get Your Free Demo' to get started!"
];
let replyIndex = 0;

function togglePopupChat() {
    popupOpen = !popupOpen;
    document.getElementById('popupFab').classList.toggle('open', popupOpen);
    document.getElementById('popupChat').classList.toggle('open', popupOpen);

    if (popupOpen && !popupGreeted) {
        popupGreeted = true;
        setTimeout(() => {
            addPopupBubble('bot', "Hey! Need a chatbot like this for your website?");
            setTimeout(() => {
                addPopupBubble('bot', "I answer client questions and capture leads — name, email, phone. All on autopilot. Try typing something!");
            }, 1200);
        }, 500);
    }
}

function addPopupBubble(role, text) {
    const container = document.getElementById('popupMessages');
    const bubble = document.createElement('div');
    bubble.classList.add('popup-bubble', role);
    bubble.textContent = text;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function sendPopupMessage() {
    const input = document.getElementById('popupInput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    addPopupBubble('user', msg);

    setTimeout(() => {
        const reply = popupReplies[replyIndex % popupReplies.length];
        replyIndex++;
        addPopupBubble('bot', reply);
    }, 800);
}

document.getElementById('popupInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendPopupMessage(); }
});
