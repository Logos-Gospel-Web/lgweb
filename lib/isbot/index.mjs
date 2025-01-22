import { isbot } from 'isbot'

let remaining = ''
process.stdin.on('data', (data) => {
    const content = remaining + data.toString('utf-8')
    const lines = content.split(/\r?\n/)
    remaining = lines.pop() || ''
    const output = lines.map((line) => (line && isbot(line) ? '1' : '0'))
    process.stdout.write(output.join(''))
})
