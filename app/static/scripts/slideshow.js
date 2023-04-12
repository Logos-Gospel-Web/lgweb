function registerSlideshow(slideshow) {
    var slides = slideshow.getElementsByClassName("slideshow__item")
    var count = slides.length
    if (count === 1) {
        return noop
    }
    var interval = 5000
    var first = slides[0]
    var last = slides[count - 1]
    var firstClone = first.cloneNode(true)
    var lastClone  = last.cloneNode(true)

    var filler = document.createElement("div")
    filler.className = "slideshow__filler"

    slideshow.insertBefore(filler, first)
    slideshow.insertBefore(lastClone, first)
    slideshow.appendChild(firstClone)

    var cursor = 0
    var moving = false
    var holding = false

    function sync() {
        filler.style.marginLeft = -(cursor + 2) * 100 + "%"
        filler.style.marginRight = "0"
    }

    sync()

    function move(by) {
        if (moving || holding) return
        moving = true
        cursor += by
        filler.style.transitionDuration = ".3s"
        sync()
        setTimeout(function() {
            filler.style.transitionDuration = ""
            if (cursor === count) {
                cursor = 0
                sync()
            } else if (cursor === -1) {
                cursor = count - 1
                sync()
            }
            moving = false
        }, 300)
    }

    function startMotion() {
        if (interval > 0) {
            return setInterval(function() { move(1) }, interval)
        } else if (interval < 0) {
            return setInterval(function() { move(-1) }, -interval)
        } else {
            return null
        }
    }

    var motion = startMotion()


    function stopMotion() {
        if (motion !== null) {
            clearInterval(motion)
            motion = null
        }
    }

    var startX = 0
    var dx = 0
    var startTime = 0

    function startSlide(x) {
        holding = true
        stopMotion()
        startX = x
        dx = 0
        startTime = Date.now()
    }

    function slide() {
        filler.style.marginRight = dx + "px"
    }

    function stopSlide() {
        var width = slideshow.getBoundingClientRect().width
        holding = false
        var endTime = Date.now()
        var speed = dx / (endTime - startTime)
        var percent = dx / width
        if (percent < 0) {
            if (percent < -0.5 || percent + (speed + 1) / 4 < -0.5) {
                move(1)
            } else {
                move(0)
            }
        } else if (percent > 0) {
            if (percent > 0.5 || percent + (speed - 1) / 4 > 0.5) {
                move(-1)
            } else {
                move(0)
            }
        } else {
            move(0)
        }
        motion = startMotion()
    }

    var unregister = createDrag({
        elem: slideshow,
        onStart: function(p) {
            if (moving || holding) return
            startSlide(p.x)
        },
        onMove: function(p) {
            if (!holding) return
            dx = p.x - startX
            slide()
        },
        onEnd: function(preventDefault) {
            if (!holding) return
            if (Math.abs(dx) > 10) preventDefault()
            stopSlide()
        },
    })

    return unregister
}

var slideshow = document.querySelector(".slideshow")
if (slideshow) {
    registerSlideshow(slideshow)
}
