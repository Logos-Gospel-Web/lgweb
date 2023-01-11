if (typeof Element !== "undefined") {
    var proto = Element.prototype
    if (!proto.matches) {
        proto.matches = proto.msMatchesSelector
    }

    if (!proto.closest) {
        proto.closest = function (s) {
            var el = this

            do {
                if (el.matches(s)) return el
                el = el.parentElement || el.parentNode
            } while (el !== null && el.nodeType === 1)

            return null
        }
    }

    if (!proto.requestFullscreen) {
        proto.requestFullscreen = proto.msRequestFullscreen
    }
}

if (!Date.now) {
    Date.now = function () {
        return (new Date).getTime()
    }
}

if (typeof Document !== "undefined") {
    var proto = Document.prototype
    if (!proto.exitFullscreen) {
        proto.exitFullscreen = proto.msExitFullscreen
    }
}
