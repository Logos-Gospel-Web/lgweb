const fakeInput = document.querySelector<HTMLInputElement>(
    '.contact__input--first',
)

if (fakeInput) {
    setInterval(() => {
        // clear fake input in case of autocomplete
        fakeInput.value = ''
    }, 1000)
}

export {}
