import { getQRCode } from './qrcode'
import { createRangeSlider } from './rangeslider'

function registerFullscreenButton() {
    document
        .querySelector('.toolbar--fullscreen')!
        .addEventListener('click', () => {
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
        })
    document.documentElement.addEventListener('fullscreenchange', () => {
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
    const main = document.querySelector('.main') as HTMLElement
    const slider = createRangeSlider({
        min: 80,
        max: 160,
        value: initialValue,
        onChange(val) {
            localStorage.setItem(localStorageKey, val + '')
            main.style.fontSize = (val / 100).toFixed(2) + 'em'
        },
    })

    const popup = document.querySelector('.fontsize')!

    document.querySelector('.fontsize__slider')!.appendChild(slider.element)

    document
        .querySelector('.fontsize__button--plus')!
        .addEventListener('click', () => {
            slider.val(slider.val() + 10)
        })

    document
        .querySelector('.fontsize__button--minus')!
        .addEventListener('click', () => {
            slider.val(slider.val() - 10)
        })

    document
        .querySelector('.toolbar--fontsize')!
        .addEventListener('click', () => {
            popup.classList.toggle('fontsize--hidden')
        })
}

function registerQrcodeButton() {
    const container = document.querySelector('.qrcode')!
    const popup = document.querySelector('.qrcode__container') as HTMLElement
    const image = document.querySelector('.qrcode__image')!
    document
        .querySelector('.toolbar--qrcode')!
        .addEventListener('click', () => {
            if (image.childNodes.length === 0) {
                const svg = getQRCode(location.href)
                image.appendChild(svg)
            }
            const qrcodeSize =
                Math.min(500, window.innerWidth, window.innerHeight) -
                100 +
                'px'
            popup.style.width = qrcodeSize
            popup.style.height = qrcodeSize
            container.classList.remove('qrcode--hidden')
        })
    document.querySelector('.qrcode__close')!.addEventListener('click', () => {
        container.classList.add('qrcode--hidden')
    })
}

function registerShareButton() {
    document.querySelector('.toolbar--share')!.addEventListener('click', () => {
        if (window.navigator && typeof navigator.share === 'function') {
            navigator.share({
                url: location.href,
                title: document.title,
            })
        }
    })
}

function registerSearchButton() {
    const container = document.querySelector('.search-bar')!
    const input = container.querySelector('.search__input') as HTMLInputElement
    document.querySelector('.toolbar--search')!.addEventListener('click', () => {
        container.classList.remove('search-bar--hidden')
        input.focus()
    })
    container.addEventListener('click', (ev) => {
        if (ev.target === ev.currentTarget) {
            container.classList.add('search-bar--hidden')
        }
    })
    document.querySelector('.search-bar__close')!.addEventListener('click', () => {
        container.classList.add('search-bar--hidden')
    })
}

registerFullscreenButton()
registerFontsizeButton()
registerQrcodeButton()
registerShareButton()
registerSearchButton()
