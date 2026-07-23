import { defineConfig } from '@rspack/cli'
import { RspackManifestPlugin } from 'rspack-manifest-plugin'

/** @type {import('@rspack/core').RspackPluginFunction} */
const NoEmitJsPlugin = (compiler) => {
    const name = 'NoEmitJsPlugin'
    compiler.hooks.thisCompilation.tap(name, (compilation) => {
        compilation.hooks.chunkAsset.tap(name, (chunk, assetName) => {
            if (assetName.endsWith('.js')) {
                const modules = compilation.chunkGraph.getChunkModules(chunk)
                if (
                    modules.every((mod) => !mod.type.startsWith('javascript/'))
                ) {
                    compilation.deleteAsset(assetName)
                }
            }
        })
    })
}

export default defineConfig((env, argv) => [
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
        output: {
            filename:
                argv.mode === 'production'
                    ? '[name].[contenthash:8].js'
                    : '[name].js',
        },
        plugins: [{ apply: NoEmitJsPlugin }, new RspackManifestPlugin()],
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
        plugins: [{ apply: NoEmitJsPlugin }],
    },
])
