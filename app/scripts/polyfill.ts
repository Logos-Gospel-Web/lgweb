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

if (!String.prototype.padStart) {
    String.prototype.padStart = function (targetLength, padString) {
        targetLength = Math.floor(targetLength) || 0
        if (targetLength < this.length) return String(this)

        padString = padString ? String(padString) : ' '

        let pad = ''
        const len = targetLength - this.length
        let i = 0
        while (pad.length < len) {
            if (!padString[i]) {
                i = 0
            }
            pad += padString[i]
            i++
        }

        return pad + String(this).slice(0)
    }
}

export {}
