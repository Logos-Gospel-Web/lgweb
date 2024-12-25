import eslint from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import eslintPluginPrettier from 'eslint-plugin-prettier/recommended'

/** @type {import('eslint').Linter.Config} */
export default tseslint.config(
    {
        ignores: ['dist', 'app/static/**'],
    },
    eslint.configs.recommended,
    tseslint.configs.strict,
    {
        rules: {
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
    eslintPluginPrettier,
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
        },
    },
    {
        files: ['app/**'],
        languageOptions: {
            globals: {
                ...globals.browser,
            },
        },
    },
    {
        ignores: ['app/**'],
        languageOptions: {
            globals: {
                ...globals.node,
            },
        },
    },
)
