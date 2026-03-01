import { listen } from './events'
import { getQRCode } from './qrcode'
import { createRangeSlider } from './rangeslider'

function registerFullscreenButton() {
    listen(
        document.querySelector<HTMLElement>('.toolbar--fullscreen')!,
        'click',
        () => {
            if (document.body.classList.contains('fullscreen')) {
                document.body.classList.remove('fullscreen')
                if (document.exitFullscreen) {
                    document.exitFullscreen()
                }
            } else {
                document.body.classList.add('fullscreen')
                if (document.documentElement.requestFullscreen) {
                    document.documentElement.requestFullscreen()
                }
            }
        },
    )
    listen(document.documentElement, 'fullscreenchange', () => {
        if (document.fullscreenElement) {
            document.body.classList.add('fullscreen')
        } else {
            document.body.classList.remove('fullscreen')
        }
    })
}

function registerFontsizeButton() {
    const localStorageKey = 'fontsize'
    const initialValue = Number(localStorage.getItem(localStorageKey)) || 100
    const main = document.querySelector<HTMLElement>('.main')!
    const slider = createRangeSlider({
        min: 80,
        max: 160,
        value: initialValue,
        onChange(val) {
            localStorage.setItem(localStorageKey, val + '')
            main.style.fontSize = (val / 100).toFixed(2) + 'em'
        },
    })

    const popup = document.querySelector<HTMLElement>('.fontsize')!

    document
        .querySelector<HTMLElement>('.fontsize__slider')!
        .appendChild(slider.element)

    listen(
        document.querySelector<HTMLElement>('.fontsize__button--plus')!,
        'click',
        () => {
            slider.val(slider.val() + 10)
        },
    )

    listen(
        document.querySelector<HTMLElement>('.fontsize__button--minus')!,
        'click',
        () => {
            slider.val(slider.val() - 10)
        },
    )

    listen(
        document.querySelector<HTMLElement>('.toolbar--fontsize')!,
        'click',
        () => {
            popup.classList.toggle('fontsize--hidden')
        },
    )
}

function registerQrcodeButton() {
    const container = document.querySelector<HTMLElement>('.qrcode')!
    const popup = document.querySelector<HTMLElement>('.qrcode__container')!
    listen(
        document.querySelector<HTMLElement>('.toolbar--qrcode')!,
        'click',
        () => {
            if (popup.childNodes.length === 1) {
                const qrcode = getQRCode(location.href)
                popup.appendChild(qrcode)
            }
            const qrcodeSize =
                Math.min(500, window.innerWidth, window.innerHeight) -
                100 +
                'px'
            popup.style.width = qrcodeSize
            popup.style.height = qrcodeSize
            container.classList.remove('qrcode--hidden')
        },
    )
    listen(
        document.querySelector<HTMLElement>('.qrcode__close')!,
        'click',
        () => {
            container.classList.add('qrcode--hidden')
        },
    )
}

function registerShareButton() {
    listen(
        document.querySelector<HTMLElement>('.toolbar--share')!,
        'click',
        () => {
            if (window.navigator && typeof navigator.share === 'function') {
                navigator.share({
                    url: location.href,
                    title: document.title,
                })
            }
        },
    )
}

function registerSearchButton() {
    const container = document.querySelector<HTMLElement>('.search-bar')!
    const input = container.querySelector<HTMLInputElement>('.search__input')!
    listen(
        document.querySelector<HTMLElement>('.toolbar--search')!,
        'click',
        () => {
            container.classList.remove('search-bar--hidden')
            input.focus()
        },
    )
    listen(container, 'click', (ev) => {
        if (ev.target === ev.currentTarget) {
            container.classList.add('search-bar--hidden')
        }
    })
    listen(
        document.querySelector<HTMLElement>('.search-bar__close')!,
        'click',
        () => {
            container.classList.add('search-bar--hidden')
        },
    )
}

registerFullscreenButton()
registerFontsizeButton()
registerQrcodeButton()
registerShareButton()
registerSearchButton()
