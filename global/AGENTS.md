# Global instructions for every project

- Keep each fact in exactly one structured source of truth - a JSON file wherever
  possible, such as a registry or a constants/labels file - and derive every other
  appearance from it: import it in code, generate configs from it, and inject it
  into docs as generated blocks. This covers hosts, ports, model names, routing,
  which tools are in use, labels, and any prose that states them.
- Never restate a fact by hand in a second place. When a fact changes, change the
  source and regenerate; never patch the copies one at a time.
- Add an entry to an existing source before writing a literal, and create a source
  as soon as a fact would otherwise appear twice.
- If a restatement genuinely cannot be generated, add a check that fails when it
  drifts from the source.

- Write code a reviewer would call beautiful, and enforce it with tooling, not memory:
  - One job per function, pure logic apart from side effects, dependencies passed in,
    no nested functions or lambdas. A function longer than about 15 lines, nested more
    than one block deep, or branching through an if/elif chain on a command or type is
    doing several jobs: split it, or dispatch through a table of named handlers.
  - Every value in one named home: configuration and contracts in JSON, SQL in `.sql`
    files reached only through the one module that owns that table or file layout.
  - Typed objects across module boundaries, validated once at the edge by declared
    schemas (typed models or JSON Schema), never hand-written checks inside functions.
  - Structured failure logs: a stable event name, correlating IDs and severity; never
    secrets or payloads; health checkable with one command.
  - Configure the linter's complexity and length limits and a check for nested
    functions and inline SQL, and run them before every commit.
- Before committing, reread the whole diff as a hostile reviewer, including every
  function you touched. Never patch lines into an ugly function: restructure it in the
  same change, or say explicitly why not.

- Write all documentation and every reply to the user in ASD-STE100 Simplified Technical English:
  PR docs, PR descriptions, READMEs, runbooks, AGENTS.md files, notebooks, and every other prose
  file or generated doc block. Be pithy. Use shorthand (fragments, tables, one-line bullets) where
  possible, so the reader can scan fast: high signal, low noise. No flavor text: no extended
  analogies, asides or restated points. Write replies terse, almost caveman-like.
  Drop filler words. This applies to explanations and discussions too. When Shaun has a
  decision to make, give only the options and a recommendation. Explain only when Shaun
  asks. Never restate or recap a point. Never use a points-then-summary template. Use
  sentences of 20 words or fewer for an instruction and 25 or fewer for a description, one
  instruction per sentence, active voice, present tense, paragraphs of six sentences or fewer.
  Use one word for one meaning, define a term where it first appears, use "must" for a required
  action, and avoid idioms, unexplained jargon, and stacks of more than three nouns.
- Finish every task the request implies before you reply. Do not stop with in-scope work open. End every reply with a Left section: the decisions Shaun owns, and the tasks that a named blocker stops, one line each, or "Nothing left". Write Left as a numbered table of ten rows or fewer, most urgent first, with a recommended answer in each row. Group minor items in one row. Name the grouped items only when Shaun asks. A row whose recommended answer is "yes" or "do it" is work, not a decision: do it before you reply. Never ask Shaun to approve or do a reversible, in-scope step. Put the result first. Keep the reply short and leave detail in the files.

- Do hands-on steps yourself. When a fix or check needs an action on this machine
  (stop or restart a local server, clear a cache, open, reload, or close a browser
  tab, change an app setting), do it with your tools and confirm the result. Do not
  give the user click-by-click steps. Ask first only when the action is destructive,
  touches another project or service, or needs credentials or administrator rights.
  When no tool can do it, say so and give the shortest steps.
- Decide it yourself. Make each choice that is reversible, in scope and within your judgement, then report it in one line. Ask only when the action is destructive, outward-facing, spends money, needs credentials, or needs a fact only Shaun knows. Never end a reply with a confirmation question for a step you can take.
- Tailnet access. Every locally run app or dev server must be reachable from every device on Shaun's tailnet. Bind it to all interfaces, or publish it with `tailscale serve`. The dev start command (for example `npm run dev`) must print only the one tailnet link to open. Allow its tailnet address (`<machine>.taila4fc43.ts.net` and its tailnet IP) in browser access rules and in login redirect settings. Report only the tailnet link. Verify the tailnet URL from a second device or with `curl` before reporting it.
- Agent sign-in. Every app must give agents a dev-only command that signs in as any test role without a password and saves a browser session file. Agents use it for every dev check and never ask Shaun to log in.
- Run browser walks at the link `npm run dev` prints (the tailnet link), not only at `localhost`. Browsers treat `localhost` as secure, so it hides failures that plain-HTTP addresses show, such as missing `crypto.randomUUID` or clipboard access.
- When the app's access address or protocol changes, rerun every save walk at the new address before reporting the change done.
- When the user corrects how you work, update the instruction files FIRST, before resuming the task, so the correction governs the rest of the work.
- Improve these instructions as you work: when a correction, a mistake worth not repeating, or a decision that should outlast the task comes up, record it where it applies (generic template in agent-skills, a project's AGENTS.md, or a directory's AGENTS.md), parsimoniously, and show the exact wording in your reply. Ask first only before you remove or weaken a rule. Report a measurement only with the method that produced it. Before editing a checkout, check for another agent working in it and never touch uncommitted work you did not make.

Project `AGENTS.md` files carry the full workflow; the canonical wording of these
rules lives in `agent-skills` (`skills/setup-project-repo/assets/AGENTS.md`).

This file is installed from `agent-skills/global/AGENTS.md`. Edit that source, then run
`scripts/install.sh`. Never edit an installed copy.
