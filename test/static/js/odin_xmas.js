let xmas_endpoint;
let tree_led_brightness = document.getElementById("tree_led_brightness");
let tree_led_mode = document.getElementById("tree_led_mode");
let tree_led_colour = document.getElementById("tree_led_colour");
let house_led_brightness = document.getElementById("house_led_brightness");
let house_led_mode = document.getElementById("house_led_mode");
let house_led_colour = document.getElementById("house_led_colour");

document.addEventListener("DOMContentLoaded", function() {

    xmas_endpoint = new AdapterEndpoint("xmas")

    xmas_endpoint.get("")
    .then(result => {
        tree_led_brightness.value = result.tree.brightness;
        tree_led_mode.value = result.tree.mode;
        tree_led_colour.value = result.tree.led_colour;
        house_led_brightness.value = result.house.brightness;
        house_led_mode.value = result.house.mode;
        house_led_colour.value = result.house.led_colour;
    })

    tree_led_brightness.addEventListener("change", evt => change_brightness(evt.target.value, "tree"));
    tree_led_mode.addEventListener("change", evt => change_mode(evt.target.value, "tree"));
    tree_led_colour.addEventListener("change", evt => change_colour(evt.target.value, "tree"));
    house_led_brightness.addEventListener("change", evt => change_brightness(evt.target.value, "house"));
    house_led_mode.addEventListener("change", evt => change_mode(evt.target.value, "house"));
    house_led_colour.addEventListener("change", evt => change_colour(evt.target.value, "house"));
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
