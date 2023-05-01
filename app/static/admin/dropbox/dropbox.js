function initializeExistingDropbox() {
    const elems = document.querySelectorAll(".lgweb-dropbox__button:empty")
    for (const elem of Array.from(elems)) {
        const isInEmpty = elem.closest(".grp-empty-form")
        if (!isInEmpty) {
            initializeDropbox(elem)
        }
    }
}

function listenForDynamicDropbox() {
    const items = document.querySelectorAll(".grp-items")
    const observer = new MutationObserver(() => initializeExistingDropbox())
    for (const item of Array.from(items)) {
        observer.observe(item, { childList: true })
    }
}

function initializeDropbox(elem) {
    var button = Dropbox.createChooseButton({
        multiselect: false,
        extensions: [".mp3"],
        folderselect: false,
        linkType: "preview",
        success: function(files) {
            elem.nextElementSibling.value = files[0].link.replace("?dl=0", "")
        }
    })
    elem.appendChild(button)
}

addEventListener('DOMContentLoaded', () => {
    initializeExistingDropbox()
    listenForDynamicDropbox()
})
