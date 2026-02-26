import eslint from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import { defineConfig } from 'eslint/config'
import prettier from 'eslint-plugin-prettier/recommended'

const browserFiles = ['app/**', 'assets/scripts/**']

/** @type {import('eslint').Linter.Config} */
export default defineConfig(
    {
        ignores: ['**/dist', 'app/static/admin/richtext/tinymce/**'],
    },
    eslint.configs.recommended,
    prettier,
    tseslint.configs.strict,
    reactHooks.configs.flat.recommended,
    {
        rules: {
            'prettier/prettier': [
                'error',
                {
                    tabWidth: 4,
                    semi: false,
                    singleQuote: true,
                    trailingComma: 'all',
                },
            ],
            eqeqeq: ['error', 'smart'],
            '@typescript-eslint/no-explicit-any': 'off',
            '@typescript-eslint/no-non-null-assertion': 'off',
            '@typescript-eslint/no-unused-vars': [
                'error',
                {
                    argsIgnorePattern: '^_',
                    varsIgnorePattern: '^_',
                    caughtErrorsIgnorePattern: '^_',
                },
            ],
        },
    },
    {
        files: browserFiles,
        languageOptions: {
            globals: {
                ...globals.browser,
            },
        },
    },
    {
        ignores: browserFiles,
        languageOptions: {
            globals: {
                ...globals.node,
            },
        },
    },
)
