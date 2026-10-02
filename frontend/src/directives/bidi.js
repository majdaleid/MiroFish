// Isolate Latin fragments in generated prose without changing copied text.
// Work on text nodes only: never replace HTML attributes, URLs or markup.
export function isolateLatinText(element) {
  const document = element.ownerDocument
  const walker = document.createTreeWalker(element, 4 /* SHOW_TEXT */)
  const nodes = []
  while (walker.nextNode()) nodes.push(walker.currentNode)
  for (const node of nodes) {
    if (node.parentElement.closest('bdi, code, pre, script, style')) continue
    const parts = node.textContent.split(/([A-Za-z][A-Za-z0-9_./:@%+#-]*(?: +[A-Za-z][A-Za-z0-9_./:@%+#-]*)*)/g)
    if (parts.length === 1) continue
    const fragment = document.createDocumentFragment()
    parts.forEach((part, index) => {
      if (index % 2) {
        const term = document.createElement('bdi')
        term.dir = 'ltr'
        term.textContent = part
        fragment.append(term)
      } else {
        fragment.append(document.createTextNode(part))
      }
    })
    node.replaceWith(fragment)
  }
}

export default { mounted: isolateLatinText, updated: isolateLatinText }
