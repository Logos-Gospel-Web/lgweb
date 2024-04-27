function initializeExistingTextarea() {
    const textareas = document.querySelectorAll(".lgweb-richtext:not([aria-hidden])")
    for (const textarea of Array.from(textareas)) {
        const isInEmpty = textarea.closest(".grp-empty-form")
        if (!isInEmpty) {
            initializeTinymce(textarea)
        }
    }
}

function listenForDynamicTextarea() {
    const items = document.querySelectorAll(".grp-items")
    const observer = new MutationObserver(() => initializeExistingTextarea())
    for (const item of Array.from(items)) {
        observer.observe(item, { childList: true })
    }
}

function getCsrfToken() {
    const element = document.querySelector("input[name=csrfmiddlewaretoken]")
    return element ? element.value : ""
}

function createFormData() {
    const form = new FormData()
    form.append("csrfmiddlewaretoken", getCsrfToken())
    return form
}

function createURLSearchParams() {
    const form = new URLSearchParams()
    form.append("csrfmiddlewaretoken", getCsrfToken())
    return form
}

async function initializeTinymce(textarea) {
    const editors = await tinymce.init({
        target: textarea,
        plugins: "code lists advlist image visualblocks help table link",
        external_plugins: {
          block: "http://example.com/block",
          import: "http://example.com/import",
          export: "http://example.com/export",
        },
        toolbar: [
            "import export | undo redo | cut copy paste | styles | forecolor | bold italic underline removeformat | alignleft aligncenter alignright alignjustify | link | bullist numlist | table | image | block | visualblocks code help",
        ],
        theme: "silver",
        skin: false,
        promotion: false,
        menubar: false,
        branding: false,
        relative_urls: false,
        remove_script_host: true,
        convert_urls: true,
        pagebreak_split_block: true,
        indent: false,
        file_picker_types: "image",
        image_dimensions: false,
        image_title: true,
        image_description: false,
        images_upload_handler: async (blobInfo) => {
            const form = createFormData()
            form.append("file", blobInfo.blob(), blobInfo.filename())
            const resp = await fetch("/adminapi/document/image", {
                method: "POST",
                body: form,
            })
            if (resp.ok) {
                const url = await resp.text()
                return url
            }
            throw new Error("Cannot upload image")
        },
        body_class: "richtext",
        content_css: "/static/compiled/richtext.css",
        fontsize_formats: "0.6em 0.65em 0.7em 0.75em 0.8em 0.9em 1em 1.25em 1.5em 1.75em 2em 2.25em 2.5em 3em 4em 5em 6em 8em",
        style_formats: [
            { title: "Paragraph", format: "paragraph" },
            { title: "Subtitle", format: "subtitle" },
            { title: "Remarks", format: "remark" },
        ],
        formats: {
            paragraph: {
                block: "p",
                attributes: { class: "" },
                wrapper: false,
            },
            subtitle: {
                block: "h2",
                attributes: { class: "" },
                wrapper: false
            },
            remark: {
                block: "p",
                attributes: { class: "remark" },
                wrapper: false,
            },
            box: {
                block: "div",
                classes: "box",
                wrapper: true,
            },
            boxInner: {
                block: "div",
                attributes: { class: "box__inner" },
                wrapper: true,
            },
        },
        table_sizing_mode: "responsive",
        table_default_styles: {},
        invalid_styles: {
            table: "width height",
            tr: "width height",
            th: "width height",
            td: "width height",
        },
    })
    const editor = editors[0]
}

function blockPlugin(editor) {
    editor.ui.registry.addButton("block", {
        icon: "unselected",
        tooltip: "Insert Text Box",
        onAction: function () {
            editor.windowManager.open({
                title: "Insert Text Box",
                body: {
                    type: "panel",
                    items: [
                    {
                        type: "selectbox",
                        name: "align",
                        label: "Align",
                        items: [
                            { value: "left", text: "Left" },
                            { value: "center", text: "Center" },
                            { value: "right", text: "Right" },
                        ],
                    },
                    {
                        type: "selectbox",
                        name: "width",
                        label: "Wrap when width smaller than",
                        items: Array.from({ length: 19 }).map((_, i) => {
                            const w = (i * 40 + 240).toString()
                            return { value: w, text: w + "px" }
                        }),
                    },
                    ],
                },
                buttons: [
                    {
                        type: "cancel",
                        text: "Close",
                    },
                    {
                        type: "submit",
                        text: "Save",
                        primary: true,
                    },
                ],
                onSubmit: function (val) {
                    const data = val.getData()
                    const box = document.createElement("div")
                    if (data.align === "center") {
                        box.className = "box box--center"
                    } else {
                        box.className = `box box--${data.align}--${data.width}`
                    }
                    const boxInner = document.createElement("div")
                    boxInner.className = "box__inner"
                    box.appendChild(boxInner)
                    const paragraph = document.createElement("p")
                    editor.insertContent(box.outerHTML + paragraph.outerHTML)
                    val.close()
                },
            })
        },
    })

    return {
        getMetadata: function () {
            return {
                url: "http://example.com/block",
                name: "Block Plugin",
            }
        },
    }
}

function importPlugin(editor) {
    editor.ui.registry.addButton("import", {
        icon: "document-properties",
        tooltip: "Import .doc",
        onAction: async function () {
            const docFile = await new Promise((resolve) => {
                const input = document.createElement("input")
                input.type = "file"
                input.accept = "application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                input.onchange = () => {
                    const files = input.files
                    if (files) {
                        const file = files[0]
                        if (file) {
                            resolve(file)
                            return
                        }
                    }
                    resolve(null)
                }
                input.click()
            })
            if (!docFile) {
              return
            }
            const ext = docFile.name.slice(docFile.name.lastIndexOf("."))
            if (ext !== ".doc" && ext !== ".docx") {
              return
            }
            const form = createFormData()
            form.append("file", docFile)
            const resp = await fetch("/adminapi/document/import", {
                method: "POST",
                body: form,
            })
            if (resp.ok) {
                const html = await resp.text()
                editor.setContent(html)
                function setValue(header, selector) {
                    const v = resp.headers.get(header)
                    if (!v) return
                    const value = Base64.decode(v)
                    let el = editor.getElement()
                    while (el) {
                        el = el.parentElement.closest("fieldset,form,div.grp-dynamic-form.inline-related")
                        if (el) {
                            const input = el.querySelector(selector)
                            input.value = value
                            return
                        }
                    }
                }
                setValue("x-data-author", "[id^=id_author],[id^=id_children-][id*=-author]")
                setValue("x-data-title", "[id^=id_title],[id^=id_children-][id*=-title]")
            }
        },
    })

    return {
        getMetadata: function () {
            return {
                url: "http://example.com/import",
                name: "Import Plugin",
            }
        },
    }
}

function exportPlugin(editor) {
    editor.ui.registry.addButton("export", {
        icon: "save",
        tooltip: "Export to .doc",
        onAction: async function () {
            const elements = {}
            let el = editor.getElement()
            while (el) {
                el = el.parentElement.closest("fieldset,form,div.grp-dynamic-form.inline-related")
                if (el) {
                    function loadValue(target, selector) {
                        if (elements[target]) return
                        const input = el.querySelector(selector)
                        if (input) {
                            elements[target] = input
                        }
                    }

                    loadValue("topic_id", "#id_parent")
                    loadValue("slug", "#id_slug")
                    loadValue("position", "#id_position,[id^=id_children-][id$=-position]")
                    loadValue("publish", "#id_publish,[id^=id_children-][id$=-publish]")
                    loadValue("title", "[id^=id_title],[id^=id_children-][id*=-title]")
                    loadValue("author", "[id^=id_author],[id^=id_children-][id*=-author]")
                }
            }
            if (!elements.title || !elements.author || !elements.position) {
                return
            }
            const data = {}
            if (elements.publish) {
                data.year = elements.publish.value.slice(0, 4)
                delete elements.publish
            } else {
                data.year = String(new Date().getFullYear())
            }
            for (const key in elements) {
                data[key] = elements[key].value
            }
            if (!data.topic_id && !data.slug) {
                return
            }
            data.language = elements.title.getAttribute("id").slice(-2)

            data.content = editor.getContent() || ""
            const form = createURLSearchParams()
            for (const key in data) {
                form.append(key, data[key])
            }
            const resp = await fetch("/adminapi/document/copy", {
                method: "POST",
                body: form,
            })
            if (resp.ok) {
                const html = await resp.blob()
                await navigator.clipboard.write([new ClipboardItem({ "text/html": html })])
            }
        },
    })

    return {
        getMetadata: function () {
            return {
                url: "http://example.com/export",
                name: "Export Plugin",
            }
        },
    }
}

function registerPlugins() {
    tinymce.PluginManager.add("block", blockPlugin)
    tinymce.PluginManager.add("import", importPlugin)
    tinymce.PluginManager.add("export", exportPlugin)
}

addEventListener('DOMContentLoaded', () => {
    registerPlugins()
    initializeExistingTextarea()
    listenForDynamicTextarea()
})
