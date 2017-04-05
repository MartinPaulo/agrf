/**
 * Created by mpaulo on 4/4/17.
 */
'use strict';
var utils = function () {

    const SPINNER_OPTIONS = {
        lines: 9, // The number of lines to draw
        length: 19, // The length of each line
        width: 5, // The line thickness
        radius: 14, // The radius of the inner circle
        color: ['black', 'white'], // #rgb or #rrggbb or array of colors
        speed: 1.9, // Rounds per second
        trail: 40, // Afterglow percentage
        className: 'spinner' // The CSS class to assign to the spinner
    };

    function launch_spinner() {
        var cover = document.getElementById("d_cover");
        cover.style.display = 'block';
        cover.style.opacity = 2;
        new Spinner(SPINNER_OPTIONS).spin(cover);
    }

    return {
        spin: launch_spinner
    }
}();