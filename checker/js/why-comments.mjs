/** Comments must start `why:`. Allows tool directives, a shebang and one file comment above the first statement. Fixer deletes the comment. */
const DIRECTIVE = /^\s*(why:|eslint|@ts-|ts-|prettier|biome|istanbul|c8|@vitest|@jest|global |#)/

function firstCodeLine(context) {
  return context.sourceCode.ast.body[0]?.loc.start.line ?? Infinity
}

function isAllowed(comment, codeStart, index) {
  return comment.type === "Shebang" || DIRECTIVE.test(comment.value) || (index === 0 && comment.loc.end.line < codeStart)
}

function jsxRange(source, comment) {
  const node = source.getNodeByRangeIndex(comment.range[0])
  return node?.type === "JSXEmptyExpression" ? node.parent.range : comment.range
}

function lineRange(text, [start, end]) {
  const lineStart = text.lastIndexOf("\n", start - 1) + 1
  const next = text.indexOf("\n", end)
  const lineEnd = next < 0 ? text.length : next + 1
  const before = text.slice(lineStart, start)
  if (text.slice(end, lineEnd).trim()) return [start, end]
  return before.trim() ? [lineStart + before.trimEnd().length, end] : [lineStart, lineEnd]
}

function removeComment(source, comment, fixer) {
  return fixer.removeRange(lineRange(source.text, jsxRange(source, comment)))
}

function reportBad(context, codeStart, comment, index) {
  if (isAllowed(comment, codeStart, index)) return
  context.report({ loc: comment.loc, message: "comment must start `why:`", fix: removeComment.bind(null, context.sourceCode, comment) })
}

function checkProgram(context) {
  context.sourceCode.getAllComments().forEach(reportBad.bind(null, context, firstCodeLine(context)))
}

function create(context) {
  return { Program: checkProgram.bind(null, context) }
}

export default { meta: { type: "suggestion", fixable: "code", schema: [] }, create }
