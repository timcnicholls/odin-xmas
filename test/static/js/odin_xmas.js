let xmas_endpoint;
let tree_led_brightness = document.getElementById("tree_led_brightness");
let tree_led_mode = document.getElementById("tree_led_mode");
let tree_led_colour = document.getElementById("tree_led_colour");
let house_led_brightness = document.getElementById("house_led_brightness");
let house_led_mode = document.getElementById("house_led_mode");
let house_led_colour = document.getElementById("house_led_colour");

// Christmas effects
function createSnowflakes() {
    const snowflakeCount = 50;
    const snowflakeChars = ['❄', '❅', '✻', '✼', '❇', '❈'];

    for (let i = 0; i < snowflakeCount; i++) {
        setTimeout(() => {
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.innerHTML = snowflakeChars[Math.floor(Math.random() * snowflakeChars.length)];
            snowflake.style.left = Math.random() * 100 + '%';
            snowflake.style.fontSize = (Math.random() * 0.8 + 0.8) + 'em';
            snowflake.style.animationDuration = (Math.random() * 3 + 2) + 's';
            snowflake.style.opacity = Math.random();
            document.body.appendChild(snowflake);

            // Remove snowflake after animation
            setTimeout(() => {
                if (snowflake.parentNode) {
                    snowflake.parentNode.removeChild(snowflake);
                }
            }, 5000);
        }, Math.random() * 10000);
    }

    // Continue creating snowflakes
    setTimeout(createSnowflakes, 5000);
}

function addChristmasLights() {
    const container = document.querySelector('.container');
    if (container) {
        container.classList.add('christmas-lights');
    }
}

function playChristmasSound(action) {
    // Create a simple audio context for festive feedback
    // This creates a gentle bell-like sound for user interactions
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Different tones for different actions
        const frequencies = {
            brightness: 523.25, // C5
            mode: 659.25,       // E5
            colour: 783.99      // G5
        };

        oscillator.frequency.value = frequencies[action] || 523.25;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    } catch (e) {
        // Audio not available, silently continue
    }
}

document.addEventListener("DOMContentLoaded", function() {

    xmas_endpoint = new AdapterEndpoint("xmas")

    // Add Christmas effects
    addChristmasLights();
    setTimeout(createSnowflakes, 1000); // Start snowflakes after page loads

    xmas_endpoint.get("")
    .then(result => {
        tree_led_brightness.value = result.tree.brightness;
        tree_led_mode.value = result.tree.mode;
        tree_led_colour.value = result.tree.led_colour;
        house_led_brightness.value = result.house.brightness;
        house_led_mode.value = result.house.mode;
        house_led_colour.value = result.house.led_colour;
    })

    tree_led_brightness.addEventListener("change", evt => {
        change_brightness(evt.target.value, "tree");
        playChristmasSound('brightness');
    });
    tree_led_mode.addEventListener("change", evt => {
        change_mode(evt.target.value, "tree");
        playChristmasSound('mode');
    });
    tree_led_colour.addEventListener("change", evt => {
        change_colour(evt.target.value, "tree");
        playChristmasSound('colour');
    });
    house_led_brightness.addEventListener("change", evt => {
        change_brightness(evt.target.value, "house");
        playChristmasSound('brightness');
    });
    house_led_mode.addEventListener("change", evt => {
        change_mode(evt.target.value, "house");
        playChristmasSound('mode');
    });
    house_led_colour.addEventListener("change", evt => {
        change_colour(evt.target.value, "house");
        playChristmasSound('colour');
    });
})

function change_brightness(value, path) {
    brightness = parseFloat(value);
    xmas_endpoint.put({'brightness': brightness}, path);
}

function change_mode(value, path) {
    xmas_endpoint.put({"mode": value}, path);
}

function change_colour(value, path) {
    xmas_endpoint.put({"led_colour": value}, path);
}
