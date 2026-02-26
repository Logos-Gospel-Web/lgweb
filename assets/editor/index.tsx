import { createRoot } from 'react-dom/client'
import RichtextEditor from './Editor'

function initializeExistingTextarea() {
    const textareas = document.querySelectorAll(
        '.lgweb-richtext-field:not([aria-hidden])',
    )
    for (const textarea of Array.from(textareas)) {
        const isInEmpty = textarea.closest('.grp-empty-form')
        if (!isInEmpty) {
            initializeEditor(textarea as HTMLTextAreaElement)
        }
    }
}

function listenForDynamicTextarea() {
    const items = document.querySelectorAll('.grp-items')
    const observer = new MutationObserver(() => initializeExistingTextarea())
    for (const item of Array.from(items)) {
        observer.observe(item, { childList: true })
    }
}

function initializeEditor(element: HTMLTextAreaElement) {
    const elem = document.createElement('div')
    const { name, value } = element
    element.replaceWith(elem)
    const root = createRoot(elem)
    root.render(<RichtextEditor name={name} content={value} />)
}

addEventListener('DOMContentLoaded', () => {
    initializeExistingTextarea()
    listenForDynamicTextarea()
})
