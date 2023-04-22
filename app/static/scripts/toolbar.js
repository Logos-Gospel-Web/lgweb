function registerFullscreenButton() {
    document.querySelector(".toolbar--fullscreen").addEventListener("click", function () {
        if (document.body.classList.contains("fullscreen")) {
            document.body.classList.remove("fullscreen")
            if (document.exitFullscreen) {
                document.exitFullscreen()
            }
        } else {
            document.body.classList.add("fullscreen")
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen()
            }
        }
    })
    document.documentElement.addEventListener("fullscreenchange", function (ev) {
        if (document.fullscreenElement) {
            document.body.classList.add("fullscreen")
        } else {
            document.body.classList.remove("fullscreen")
        }
    })
}

function registerFontsizeButton() {
    var localStorageKey = "fontsize"
    var initialValue = Number(localStorage.getItem(localStorageKey)) || 100
    var main = document.querySelector(".main")
    var slider = createRangeSlider({
        min: 80,
        max: 160,
        value: initialValue,
        onChange: function(val) {
            localStorage.setItem(localStorageKey, val + "")
            main.style.fontSize = (val / 100).toFixed(2) + "em"
        },
    })

    var popup = document.querySelector(".fontsize")

    document.querySelector(".fontsize__slider").appendChild(slider.element)

    document.querySelector(".fontsize__button--plus").addEventListener("click", function () {
        slider.val(slider.val() + 10)
    })

    document.querySelector(".fontsize__button--minus").addEventListener("click", function () {
        slider.val(slider.val() - 10)
    })

    document.querySelector(".toolbar--fontsize").addEventListener("click", function () {
        popup.classList.toggle("fontsize--hidden")
    })
}

function registerQrcodeButton() {
    var container = document.querySelector(".qrcode")
    var popup = document.querySelector(".qrcode__container")
    var image = document.querySelector(".qrcode__image")
    document.querySelector(".toolbar--qrcode").addEventListener("click", function () {
        if (image.childNodes.length === 0) {
            var svg = QRCode(location.href)
            image.appendChild(svg)
        }
        var qrcodeSize = Math.min(500, window.innerWidth, window.innerHeight) - 100 + "px"
        popup.style.width = qrcodeSize
        popup.style.height = qrcodeSize
        container.classList.remove("qrcode--hidden")
    })
    document.querySelector(".qrcode__close").addEventListener("click", function () {
        container.classList.add("qrcode--hidden")
    })
}

function registerShareButton() {
    document.querySelector(".toolbar--share").addEventListener("click", function () {
        if (window.navigator && window.navigator.share) {
            navigator.share({
                url: location.href,
                title: document.title,
            })
        }
    })
}

registerFullscreenButton()
registerFontsizeButton()
registerQrcodeButton()
registerShareButton()
