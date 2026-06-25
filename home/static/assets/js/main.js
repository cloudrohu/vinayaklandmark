document.addEventListener("DOMContentLoaded", function () {

    const openBtn = document.getElementById("openLegacy");
    const closeBtn = document.getElementById("closeLegacy");

    const legacySection = document.getElementById("legacyScroll");
    const scrollPaper = document.getElementById("scrollPaper");

    openBtn.addEventListener("click", () => {

        legacySection.classList.remove("hidden");

        setTimeout(() => {

            scrollPaper.classList.remove(
                "scale-y-0",
                "opacity-0",
                "rotate-[-2deg]"
            );

            scrollPaper.classList.add(
                "scale-y-100",
                "opacity-100",
                "rotate-0"
            );

            legacySection.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        }, 100);

    });

    closeBtn.addEventListener("click", () => {

        scrollPaper.classList.remove(
            "scale-y-100",
            "opacity-100",
            "rotate-0"
        );

        scrollPaper.classList.add(
            "scale-y-0",
            "opacity-0",
            "rotate-[-2deg]"
        );

        setTimeout(() => {
            legacySection.classList.add("hidden");
        }, 1000);

    });

});
new Swiper(".projectSwiper", {
    loop: true,
    speed: 900,
    spaceBetween: 30,

    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },

    autoplay: {
        delay: 3500,
        disableOnInteraction: false,
    },

    breakpoints: {
        0: {
            slidesPerView: 1
        },
        768: {
            slidesPerView: 2
        },
        1024: {
            slidesPerView: 3
        }
    }
});