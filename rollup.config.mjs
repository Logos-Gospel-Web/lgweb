import { babel } from '@rollup/plugin-babel'
import { nodeResolve } from '@rollup/plugin-node-resolve'
import terser from '@rollup/plugin-terser'

const isProd = process.env.MODE === 'production'

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
        babel({
            extensions: ['.js', '.ts'],
            babelHelpers: 'bundled',
        }),
        isProd && terser(),
    ],
}
