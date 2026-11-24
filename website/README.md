# Website

Docs are sourced from the repository `docs/` directory (`docusaurus.config.ts`
`docs.path: '../docs'`). The unused Docusaurus classic-template files under
`website/docs/` were removed.

## Installation

```bash
npm ci
```

CI installs with `npm ci` from `package-lock.json`, so use npm.

## Local Development

```bash
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run typecheck
npm run build
```

`npm run build` generates static content into the `build` directory. CI runs both
commands on every pull request that touches `docs/` or `website/`.

## Deployment

Do not deploy by hand. `.github/workflows/deploy-docs.yml` builds the site on every push
to `main` that touches `docs/`, `website/` or the workflow, uploads `website/build` as a
GitHub Pages artifact and publishes it with `actions/deploy-pages`. Run it manually with
*Run workflow* (`workflow_dispatch`). There is no `gh-pages` branch.
