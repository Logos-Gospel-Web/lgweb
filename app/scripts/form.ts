const fakeInputs = document.getElementsByClassName('contact__input--first')

for (let i = 0, n = fakeInputs.length; i < n; i += 1) {
    const fakeInput = fakeInputs[i]
    setInterval(() => {
        // clear fake input in case of autocomplete
        ;(fakeInput as HTMLInputElement).value = ''
    }, 1000)
}

export {}
