import { defineConfig } from '@rspack/cli'

export default defineConfig([
    {
        extends: './rspack.base.config.mjs',
        target: 'browserslist',
        entry: {
            script: './scripts/index.ts',
            sw: './scripts/service.worker.ts',
            style: './styles/index.scss',
            noscript: './styles/noscript.scss',
            error: './styles/error.scss',
            statistics: './styles/statistics.scss',
        },
    },
    {
        extends: './rspack.base.config.mjs',
        target: 'browserslist:last 2 chrome versions',
        entry: {
            richtext_editor_script: './editor/index.tsx',
            richtext_editor_style: './editor/index.scss',
        },
        performance: {
            maxAssetSize: 1e9,
            maxEntrypointSize: 1e9,
        },
    },
])
