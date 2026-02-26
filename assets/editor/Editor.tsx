import { Editor, mergeAttributes, Node } from '@tiptap/core'
import { useEditor, EditorContent, useEditorState } from '@tiptap/react'
import Image from '@tiptap/extension-image'
import { TableKit } from '@tiptap/extension-table'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import { Color, TextStyle } from '@tiptap/extension-text-style'
import TextAlign from '@tiptap/extension-text-align'
import Paragraph from '@tiptap/extension-paragraph'
import StarterKit from '@tiptap/starter-kit'
import FileHandler from '@tiptap/extension-file-handler'
import InvisibleCharacters from '@tiptap/extension-invisible-characters'
import { useCallback, useState } from 'react'
import { decode } from 'js-base64'
import {
    MdUndo,
    MdRedo,
    MdImage,
    MdFormatBold,
    MdFormatStrikethrough,
    MdFormatItalic,
    MdFormatUnderlined,
    MdSuperscript,
    MdSubscript,
    MdFormatClear,
    MdFormatAlignLeft,
    MdFormatAlignCenter,
    MdFormatAlignRight,
    MdFormatAlignJustify,
    MdHorizontalRule,
    MdLink,
    MdLinkOff,
    MdFormatListBulleted,
    MdFormatListNumbered,
    MdOutlineTableChart,
    MdFormatColorText,
    MdOutlineRectangle,
    MdDocumentScanner,
    MdFileCopy,
    MdSpaceBar,
} from 'react-icons/md'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from './components/tiptap-ui-primitive/dropdown-menu'

function getCsrfToken() {
    const element = document.querySelector(
        'input[name=csrfmiddlewaretoken]',
    ) as HTMLInputElement
    return element ? element.value : ''
}

function createFormData() {
    const form = new FormData()
    form.append('csrfmiddlewaretoken', getCsrfToken())
    return form
}

function createURLSearchParams() {
    const form = new URLSearchParams()
    form.append('csrfmiddlewaretoken', getCsrfToken())
    return form
}

async function uploadImage(file: File) {
    const form = createFormData()
    form.append('file', file, file.name)
    const resp = await fetch('/adminapi/document/image', {
        method: 'POST',
        body: form,
    })
    if (resp.ok) {
        const url = await resp.text()
        return url
    }
    return ''
}

async function uploadImages(files: File[]) {
    return Promise.all(files.map(uploadImage)).then((urls) =>
        urls.filter((url) => url),
    )
}

const CustomParagraph = Paragraph.extend({
    parseHTML() {
        return [
            {
                tag: 'p',
                getAttrs: (node) => node.className === '' && null,
            },
        ]
    },
    addKeyboardShortcuts() {
        return {
            'Mod-Alt-1': () => this.editor.commands.setNode('paragraph'),
        }
    },
})

const Remark = Paragraph.extend({
    name: 'remark',
    renderHTML({ HTMLAttributes }) {
        return ['p', mergeAttributes(HTMLAttributes, { class: 'remark' }), 0]
    },
    parseHTML() {
        return [
            {
                tag: 'p',
                getAttrs: (node) => node.className === 'remark' && null,
            },
        ]
    },
    addKeyboardShortcuts() {
        return {
            'Mod-Alt-3': () => this.editor.commands.setNode('remark'),
        }
    },
})

const MessageEnd = Paragraph.extend({
    name: 'msgend',
    renderHTML({ HTMLAttributes }) {
        return ['p', mergeAttributes(HTMLAttributes, { class: 'msgend' }), 0]
    },
    parseHTML() {
        return [
            {
                tag: 'p',
                getAttrs: (node) => node.className === 'msgend' && null,
            },
        ]
    },
    addKeyboardShortcuts() {
        return {
            'Mod-Alt-4': () => this.editor.commands.setNode('msgend'),
        }
    },
})

function insertImagesToEditor(
    editor: Editor,
    files: File[],
    pos: number = editor.state.selection.anchor,
) {
    uploadImages(files).then((urls) => {
        urls.reverse()
        for (const url of urls) {
            editor
                .chain()
                .insertContentAt(pos, {
                    type: 'image',
                    attrs: { src: url },
                })
                .focus()
                .run()
        }
    })
}

const CustomFileHandler = FileHandler.configure({
    allowedMimeTypes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
    onDrop: insertImagesToEditor,
    onPaste: (editor, files, htmlContent) => {
        if (htmlContent) {
            return false
        }
        insertImagesToEditor(editor, files)
    },
})

function constructBoxClass(align: string, offset: number) {
    if (align === 'center') {
        return 'box'
    }
    return `box box--${align}--${offset}`
}

async function importDoc(editor: Editor) {
    const docFile = await new Promise<File | null>((resolve) => {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept =
            'application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document'
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
    const ext = docFile.name.slice(docFile.name.lastIndexOf('.'))
    if (ext !== '.doc' && ext !== '.docx') {
        return
    }
    const form = createFormData()
    form.append('file', docFile)
    const resp = await fetch('/adminapi/document/import', {
        method: 'POST',
        body: form,
    })
    if (resp.ok) {
        const html = await resp.text()
        editor.commands.setContent(html)
        function setValue(header: string, selector: string) {
            const v = resp.headers.get(header)
            if (!v) return
            const value = decode(v)
            let el = editor.view.dom
            while (el) {
                el = el.parentElement!.closest(
                    'fieldset,form,div.grp-dynamic-form.inline-related',
                ) as HTMLElement
                if (el) {
                    const input = el.querySelector(selector) as HTMLInputElement
                    input.value = value
                    return
                }
            }
        }
        setValue(
            'x-data-author',
            '[id^=id_author],[id^=id_children-][id*=-author]',
        )
        setValue(
            'x-data-title',
            '[id^=id_title],[id^=id_children-][id*=-title]',
        )
    }
}

async function exportDoc(editor: Editor) {
    const elements: Record<string, HTMLInputElement> = {}
    let el = editor.view.dom
    while (el) {
        el = el.parentElement!.closest(
            'fieldset,form,div.grp-dynamic-form.inline-related',
        ) as HTMLElement
        if (el) {
            function loadValue(target: string, selector: string) {
                if (elements[target]) return
                const input = el.querySelector(selector)
                if (input) {
                    elements[target] = input as HTMLInputElement
                }
            }

            loadValue('topic_id', '#id_parent')
            loadValue('slug', '#id_slug')
            loadValue(
                'position',
                '#id_position,[id^=id_children-][id$=-position]',
            )
            loadValue('publish', '#id_publish,[id^=id_children-][id$=-publish]')
            loadValue('title', '[id^=id_title],[id^=id_children-][id*=-title]')
            loadValue(
                'author',
                '[id^=id_author],[id^=id_children-][id*=-author]',
            )
        }
    }
    if (!elements.title || !elements.author || !elements.position) {
        return
    }
    const data: any = {}
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
    data.language = elements.title.getAttribute('id')!.slice(-2)

    data.content = editor.getHTML()
    const form = createURLSearchParams()
    for (const key in data) {
        form.append(key, data[key])
    }
    const resp = await fetch('/adminapi/document/copy', {
        method: 'POST',
        body: form,
    })
    if (resp.ok) {
        const html = await resp.blob()
        await navigator.clipboard.write([
            new ClipboardItem({ 'text/html': html }),
        ])
    }
}

const BOX_ALIGN_VALUES = ['left', 'center', 'right']
const Box = Node.create({
    name: 'box',
    group: 'block',
    content: 'block*',
    addAttributes() {
        return {
            align: {
                isRequired: true,
                rendered: false,
                validate(value: string) {
                    return BOX_ALIGN_VALUES.includes(value)
                },
                parseHTML(elem) {
                    const { className } = elem
                    if (className.includes('box--left--')) return 'left'
                    if (className.includes('box--right--')) return 'right'
                    return 'center'
                },
            },
            breakpoint: {
                isRequired: true,
                rendered: false,
                validate(value: number) {
                    return Number.isInteger(value)
                },
                parseHTML(elem) {
                    const { className } = elem
                    const index = className.lastIndexOf('--')
                    if (index === -1) return 0
                    return Number(className.slice(index + 2))
                },
            },
        }
    },

    renderHTML({ node, HTMLAttributes }) {
        return [
            'div',
            mergeAttributes(HTMLAttributes, {
                class: constructBoxClass(
                    node.attrs.align,
                    node.attrs.breakpoint,
                ),
            }),
            [
                'div',
                {
                    class: 'box__inner',
                },
                0,
            ],
        ]
    },

    parseHTML() {
        return [
            {
                tag: 'div',
                getAttrs: (node) => node.classList.contains('box') && null,
            },
        ]
    },
})

const EMPTY_PARAGRAPH = '<p></p>'

const paraStates = Object.entries({
    paragraph: 'Paragraph',
    heading: 'Heading',
    remark: 'Remark',
    msgend: 'Topic End',
})

const Toolbar: React.FunctionComponent<{ editor: Editor }> = ({ editor }) => {
    const editorState = useEditorState({
        editor,
        selector: ({ editor }) => ({
            paraState:
                paraStates.find(([state]) => editor.isActive(state))?.[1] ||
                'Paragraph',
            currentColor: editor.getAttributes('textStyle').color || '#000000',
        }),
    })

    const setLink = useCallback(() => {
        const previousUrl = editor.getAttributes('link').href
        const url = window.prompt('URL', previousUrl)
        if (url === null) return
        if (url === '') {
            editor.chain().focus().extendMarkRange('link').unsetLink().run()
            return
        }
        try {
            editor
                .chain()
                .focus()
                .extendMarkRange('link')
                .setLink({ href: url })
                .run()
        } catch (e: any) {
            alert(e.message)
        }
    }, [editor])

    const addImage = useCallback(() => {
        const input = document.createElement('input')
        input.type = 'file'
        input.multiple = true
        input.accept = 'image/png,image/jpeg,image/gif,image/webp'
        input.onchange = () => {
            if (input.files) {
                insertImagesToEditor(editor, Array.from(input.files))
            }
        }
        input.click()
    }, [editor])

    const addBox = useCallback(
        (align: 'left' | 'center' | 'right') => {
            if (align === 'center') {
                editor.commands.insertContent({
                    type: 'box',
                    attrs: { align, breakpoint: 0 },
                    content: [
                        {
                            type: 'paragraph',
                        },
                    ],
                })
            } else {
                const breakpoint = Number(
                    window.prompt(
                        'Breakpoint (must be between 240 and 960, and a multiple of 40)',
                    ),
                )
                if (!Number.isInteger(breakpoint)) return
                if (breakpoint % 40 !== 0) return
                if (breakpoint < 240) return
                if (breakpoint > 960) return
                editor.commands.insertContent({
                    type: 'box',
                    attrs: { align, breakpoint },
                    content: [
                        {
                            type: 'paragraph',
                        },
                    ],
                })
            }
        },
        [editor],
    )

    return (
        <div className="lgweb-richtext-toolbar">
            <MdDocumentScanner
                onClick={() => importDoc(editor)}
                title="Import Doc"
            />
            <MdFileCopy
                onClick={() => exportDoc(editor)}
                title="Copy to clipboard (paste on a Word file)"
            />
            <hr />
            <MdHorizontalRule
                title="Preview (only used in blog layout)"
                onClick={() => editor.chain().focus().setHorizontalRule().run()}
            />
            <hr />
            <MdUndo onClick={() => editor.commands.undo()} title="Undo" />
            <MdRedo onClick={() => editor.commands.redo()} title="Redo" />
            <hr />
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <div
                        className="lgweb-richtext-button"
                        style={{ width: '120px', border: '1px solid #ccc' }}
                    >
                        {editorState.paraState}
                    </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                    {paraStates.map(([key, label]) => (
                        <DropdownMenuItem
                            key={key}
                            onClick={() => editor.commands.setNode(key)}
                        >
                            {label}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuContent>
            </DropdownMenu>
            <hr />
            <MdFormatBold
                onClick={() => editor.commands.toggleBold()}
                title="Bold"
            />
            <MdFormatItalic
                onClick={() => editor.commands.toggleItalic()}
                title="Italic"
            />
            <MdFormatUnderlined
                onClick={() => editor.commands.toggleUnderline()}
                title="Underline"
            />
            <MdFormatStrikethrough
                onClick={() => editor.commands.toggleStrike()}
                title="Strikethrough"
            />
            <MdSubscript
                onClick={() => editor.commands.toggleSubscript()}
                title="Subscript"
            />
            <MdSuperscript
                onClick={() => editor.commands.toggleSuperscript()}
                title="Superscript"
            />
            <label className="lgweb-color-picker">
                <MdFormatColorText title="Color" />
                <input
                    type="color"
                    value={editorState.currentColor}
                    onChange={(ev) =>
                        editor
                            .chain()
                            .focus()
                            .setColor(ev.currentTarget.value)
                            .run()
                    }
                />
            </label>
            <MdFormatClear
                onClick={() => editor.commands.unsetAllMarks()}
                title="Clear format"
            />
            <hr />
            <MdFormatAlignLeft
                title="Align left"
                onClick={() => editor.commands.setTextAlign('left')}
            />
            <MdFormatAlignCenter
                title="Align center"
                onClick={() => editor.commands.setTextAlign('center')}
            />
            <MdFormatAlignRight
                title="Align right"
                onClick={() => editor.commands.setTextAlign('right')}
            />
            <MdFormatAlignJustify
                title="Justify"
                onClick={() => editor.commands.setTextAlign('justify')}
            />
            <MdFormatClear
                title="Clear align"
                onClick={() => editor.commands.unsetTextAlign()}
            />
            <hr />
            <MdLink title="Add link" onClick={setLink} />
            <MdLinkOff
                title="Remove link"
                onClick={() => editor.chain().focus().unsetLink().run()}
            />
            <hr />
            <MdFormatListBulleted
                title="Bullet list"
                onClick={() => editor.chain().focus().toggleBulletList().run()}
            />
            <MdFormatListNumbered
                title="Numbered list"
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
            />
            <hr />
            <MdImage title="Image" onClick={addImage} />
            <hr />
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <MdOutlineTableChart title="Table" />
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                    <DropdownMenuItem
                        onClick={() =>
                            editor
                                .chain()
                                .focus()
                                .insertTable({
                                    rows: 3,
                                    cols: 3,
                                    withHeaderRow: true,
                                })
                                .run()
                        }
                    >
                        Insert Table
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().addColumnBefore().run()
                        }
                    >
                        Add column before
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().addColumnAfter().run()
                        }
                    >
                        Add column after
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().deleteColumn().run()
                        }
                    >
                        Delete column
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().addRowBefore().run()
                        }
                    >
                        Add row before
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().addRowAfter().run()
                        }
                    >
                        Add row after
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() => editor.chain().focus().deleteRow().run()}
                    >
                        Delete row
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().deleteTable().run()
                        }
                    >
                        Delete table
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().mergeCells().run()
                        }
                    >
                        Merge cells
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() => editor.chain().focus().splitCell().run()}
                    >
                        Split cell
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().toggleHeaderRow().run()
                        }
                    >
                        Toggle header row
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().toggleHeaderCell().run()
                        }
                    >
                        Toggle header cell
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() => editor.chain().focus().fixTables().run()}
                    >
                        Fix table
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() =>
                            editor.chain().focus().deleteTable().run()
                        }
                    >
                        Delete table
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
            <hr />
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <MdOutlineRectangle title="Box" />
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                    <DropdownMenuItem onClick={() => addBox('left')}>
                        Left
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => addBox('center')}>
                        Center
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => addBox('right')}>
                        Right
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
            <hr />
            <MdSpaceBar
                title="Show hidden characters"
                onClick={() => editor.commands.toggleInvisibleCharacters()}
            />
        </div>
    )
}

const RichtextEditor: React.FunctionComponent<{
    name: string
    content: string
}> = (props) => {
    const [content, setContent] = useState(props.content)
    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [2],
                },
                blockquote: false,
                codeBlock: false,
                trailingNode: {
                    notAfter: ['paragraph', 'remark', 'heading'],
                },
                paragraph: false,
                link: {
                    defaultProtocol: 'https',
                    openOnClick: false,
                },
            }),
            CustomParagraph,
            Image.configure({
                inline: true,
            }),
            TableKit.configure({
                table: {
                    cellMinWidth: 0,
                    lastColumnResizable: false,
                },
            }),
            Subscript,
            Superscript,
            TextStyle,
            Color,
            TextAlign.configure({
                types: ['heading', 'paragraph', 'remark'],
            }),
            Remark,
            MessageEnd,
            CustomFileHandler,
            Box,
            InvisibleCharacters.configure({
                visible: false,
            }),
        ],
        injectCSS: false,
        editorProps: {
            attributes: {
                class: 'lgweb-richtext-content',
            },
        },
        content: props.content,
        onUpdate({ editor }) {
            let html = editor.getHTML()
            while (html.endsWith(EMPTY_PARAGRAPH)) {
                html = html.slice(0, -EMPTY_PARAGRAPH.length)
            }
            setContent(html)
        },
    })

    return (
        <>
            <Toolbar editor={editor} />
            <EditorContent editor={editor} />
            <textarea
                name={props.name}
                value={content}
                readOnly
                style={{ display: 'none' }}
            />
        </>
    )
}

export default RichtextEditor
