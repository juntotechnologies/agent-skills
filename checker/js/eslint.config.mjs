/** Shared code rules for JS and TS. A repo's own ESLint config still runs for its local rules. */
import tseslint from "typescript-eslint"
import whyComments from "./why-comments.mjs"

const NESTED = { selector: ":function :function", message: "move to top level" }
const CODE = ["**/*.{js,mjs,cjs,ts}"]
const VIEWS = ["**/*.{jsx,tsx}"]
const TESTS = ["**/tests/**", "**/test/**", "**/*.test.*", "**/*.spec.*"]
const local = { rules: { "why-comments": whyComments } }

export default [
  { files: [...CODE, ...VIEWS], plugins: { local }, languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } } },
  { files: [...CODE, ...VIEWS], rules: { "local/why-comments": "error", complexity: ["error", 5], "max-depth": ["error", 1], "max-params": ["error", 6] } },
  { files: CODE, rules: { "max-lines-per-function": ["error", { max: 15, skipBlankLines: true, skipComments: true }], "no-restricted-syntax": ["error", NESTED] } },
  { files: TESTS, rules: { "max-lines-per-function": "off", "no-restricted-syntax": "off" } },
]
