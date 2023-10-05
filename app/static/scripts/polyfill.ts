if (typeof Element !== 'undefined') {
    const proto = Element.prototype as any
    if (!proto.matches) {
        proto.matches = proto.msMatchesSelector
    }

    if (!proto.closest) {
        proto.closest = function (s: any) {
            // eslint-disable-next-line @typescript-eslint/no-this-alias
            let el = this

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
        return new Date().getTime()
    }
}

if (typeof Document !== 'undefined') {
    const proto = Document.prototype as any
    if (!proto.exitFullscreen) {
        proto.exitFullscreen = proto.msExitFullscreen
    }
}
