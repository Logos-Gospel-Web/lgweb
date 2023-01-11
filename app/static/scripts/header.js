delegate(".header__offcanvas__inner", "click", function() {
    var header = document.querySelector(".header")
    header.classList.toggle("header--expanded")
})

delegate(".nav__expand", "click", function(ev) {
    ev.preventDefault()
    var target = ev.currentTarget
    var list = target.nextSibling ? target.nextSibling : target.parentElement.nextSibling
    var item = list.parentElement

    var expanded = item.classList.toggle("nav__item--expanded")
    list.style.maxHeight = expanded ? list.children.length * 48 + "px" : ""
})

delegate(".header__title__link, a.nav__item__inner > .nav__item__text, a.nav__subitem__inner", "click", function() {
    var header = document.querySelector(".header")
    header.classList.remove("header--expanded")
})
