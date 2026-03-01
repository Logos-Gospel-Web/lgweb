import { listen, listenMany } from './events'

const header = document.querySelector<HTMLElement>('.header')!
const offcanvas = document.querySelector<HTMLElement>(
    '.header__offcanvas__inner',
)!

listen(offcanvas, 'click', () => {
    header.classList.toggle('header--expanded')
})

const expandElems = document.querySelectorAll<HTMLElement>('.nav__expand')
listenMany(expandElems, 'click', (ev) => {
    ev.preventDefault()
    const target = ev.currentTarget as HTMLElement
    const list = (target.nextSibling ||
        target.parentElement!.nextSibling) as HTMLElement
    const item = list.parentElement!

    const expanded = item.classList.toggle('nav__item--expanded')
    list.style.maxHeight = expanded ? list.children.length * 48 + 'px' : ''
})

const closeElems = document.querySelectorAll<HTMLElement>(
    '.header__title__link, a.nav__item__inner > .nav__item__text, a.nav__subitem__inner',
)
listenMany(closeElems, 'click', () => {
    header.classList.remove('header--expanded')
})
