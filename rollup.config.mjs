import path from 'path'
import { babel } from '@rollup/plugin-babel'
import alias from '@rollup/plugin-alias'
import { nodeResolve } from '@rollup/plugin-node-resolve'
import terser from '@rollup/plugin-terser'

const isProd = process.env.MODE === 'production'

function resolve(...args) {
    return path.resolve('..', '..', ...args)
}

/** @type {import('rollup').RollupOptions} */
export default {
    output: {
        format: 'iife',
    },
    plugins: [
        nodeResolve({
            browser: true,
            extensions: ['.js', '.ts'],
        }),
        alias({
            entries: [
                { find: '@', replacement: resolve('app', 'static', 'scripts') },
            ],
        }),
        babel({
            extensions: ['.js', '.ts'],
            babelHelpers: 'bundled',
        }),
        isProd && terser(),
    ],
}
