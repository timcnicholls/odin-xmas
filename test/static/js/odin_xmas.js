let xmas_endpoint;
let led_brightness = document.getElementById("led_brightness");
let led_mode = document.getElementById("led_mode");
let led_colour = document.getElementById("led_colour");

document.addEventListener("DOMContentLoaded", function() {

    xmas_endpoint = new AdapterEndpoint("xmas")

    xmas_endpoint.get("")
    .then(result => {
        led_brightness.value = result.brightness;
        led_mode.value = result.mode;
        led_colour.value = result.led_colour;
    })

    led_brightness.addEventListener("input", change_brightness);
    led_mode.addEventListener("change", change_mode);
    led_colour.addEventListener("change", change_colour);
})

function change_brightness() {
    brightness = parseFloat(led_brightness.value);
    xmas_endpoint.put({'brightness': brightness});
}

function change_mode() {
    xmas_endpoint.put({"mode": led_mode.value});
}

function change_colour() {
    xmas_endpoint.put({"led_colour": led_colour.value});
}