        // Countdown timer
        function startCountdown(duration, display) {
            var timer = duration, minutes, seconds;
            var countdown = setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                display.textContent = minutes + ":" + seconds;

                if (--timer < 0) {
                    clearInterval(countdown);
                    display.textContent = "Time expired";
                    // You could redirect or disable buttons here
                }
            }, 1000);
        }

        window.onload = function () {
            var twoMinutes = 60 * 2,
                display = document.querySelector('#countdown');
            startCountdown(twoMinutes, display);
        };
