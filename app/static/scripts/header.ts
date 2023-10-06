import { delegate } from './events'

delegate('.header__offcanvas__inner', 'click', () => {
    const header = document.querySelector('.header')!
    header.classList.toggle('header--expanded')
})

delegate('.nav__expand', 'click', (ev) => {
    ev.preventDefault()
    const target = ev.currentTarget as HTMLElement
    const list = (
        target.nextSibling
            ? target.nextSibling
            : target.parentElement!.nextSibling
    ) as HTMLElement
    const item = list.parentElement!

    const expanded = item.classList.toggle('nav__item--expanded')
    list.style.maxHeight = expanded ? list.children.length * 48 + 'px' : ''
})

delegate(
    '.header__title__link, a.nav__item__inner > .nav__item__text, a.nav__subitem__inner',
    'click',
    () => {
        const header = document.querySelector('.header')!
        header.classList.remove('header--expanded')
    },
)
