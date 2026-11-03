/** Comments must start `why:`. Allows tool directives, a shebang and one file comment above the first statement. */
const DIRECTIVE = /^\s*(why:|eslint|@ts-|ts-|prettier|biome|istanbul|c8|@vitest|@jest|global |#)/

function firstCodeLine(context) {
  return context.sourceCode.ast.body[0]?.loc.start.line ?? Infinity
}

function isAllowed(comment, codeStart, index) {
  return comment.type === "Shebang" || DIRECTIVE.test(comment.value) || (index === 0 && comment.loc.end.line < codeStart)
}

function reportBad(context, codeStart, comment, index) {
  if (!isAllowed(comment, codeStart, index)) context.report({ loc: comment.loc, message: "comment must start `why:`" })
}

function checkProgram(context) {
  context.sourceCode.getAllComments().forEach(reportBad.bind(null, context, firstCodeLine(context)))
}

function create(context) {
  return { Program: checkProgram.bind(null, context) }
}

export default { meta: { type: "suggestion", schema: [] }, create }
