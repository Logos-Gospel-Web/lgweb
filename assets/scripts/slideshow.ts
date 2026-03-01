import { createDrag } from './drag'
import { listenMany } from './events'

function registerSlideshow(slideshow: HTMLElement) {
    const slides = slideshow.getElementsByClassName('slideshow__item')
    const count = slides.length
    if (count === 1) return
    const interval = 5000
    const first = slides[0]!
    const last = slides[count - 1]!
    const firstClone = first.cloneNode(true)
    const lastClone = last.cloneNode(true)

    const filler = document.createElement('div')
    filler.className = 'slideshow__filler'

    slideshow.insertBefore(filler, first)
    slideshow.insertBefore(lastClone, first)
    slideshow.appendChild(firstClone)

    let cursor = 0
    let moving = false
    let holding = false

    function sync() {
        filler.style.marginLeft = -(cursor + 2) * 100 + '%'
        filler.style.marginRight = '0'
    }

    sync()

    function move(by: number) {
        if (moving || holding) return
        moving = true
        cursor += by
        filler.style.transitionDuration = '.3s'
        sync()
        setTimeout(() => {
            filler.style.transitionDuration = ''
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
            return setInterval(() => {
                move(1)
            }, interval)
        } else if (interval < 0) {
            return setInterval(() => {
                move(-1)
            }, -interval)
        } else {
            return null
        }
    }

    let motion = startMotion()

    function stopMotion() {
        if (motion !== null) {
            clearInterval(motion)
            motion = null
        }
    }

    let startX = 0
    let dx = 0
    let startTime = 0

    function startSlide(x: number) {
        holding = true
        stopMotion()
        startX = x
        dx = 0
        startTime = Date.now()
    }

    function slide() {
        filler.style.marginRight = dx + 'px'
    }

    function stopSlide() {
        const width = slideshow.getBoundingClientRect().width
        holding = false
        const endTime = Date.now()
        const speed = dx / (endTime - startTime)
        const percent = dx / width
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
        if (motion === null) {
            motion = startMotion()
        }
    }

    createDrag({
        elem: slideshow,
        onStart(p) {
            if (moving || holding) return
            startSlide(p.x)
        },
        onMove(p) {
            if (!holding) return
            dx = p.x - startX
            slide()
        },
        onEnd(preventDefault) {
            if (!holding) return
            if (Math.abs(dx) > 10) preventDefault()
            setTimeout(stopSlide, 0)
        },
    })

    const anchors = slideshow.querySelectorAll('a')
    const anchorPrevent = (ev: Event) => {
        if (holding && Math.abs(dx) > 10) {
            ev.preventDefault()
            ev.stopPropagation()
        }
    }
    listenMany(anchors, 'click', anchorPrevent)
}

const slideshow = document.querySelector<HTMLElement>('.slideshow')
if (slideshow) {
    registerSlideshow(slideshow)
}
