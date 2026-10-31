# Static deployment / 静态部署

The viewer needs no server-side code, API token, database or build service.

## GitHub Pages

The project's online gallery is at
**[yuhua0987.github.io/polaroid-camera-archive](https://yuhua0987.github.io/polaroid-camera-archive/)**.

To deploy this repository or your own fork:

1. In the repository, open **Settings → Pages** and choose **GitHub Actions** as the source.
2. Open **Actions → Deploy gallery to Pages → Run workflow**, selecting `main`.
3. Wait for the deployment to succeed, then open the URL shown by the deployment job.

The Pages workflow is manual so forks do not attempt deployment before their
owners enable Pages. The normal validation workflow runs on pushes and pull requests.
Publication is complete only after GitHub reports the Pages deployment URL and
that URL serves the built gallery.

## Another static host

```sh
python3 tools/validate.py
python3 tools/build.py
```

Upload the contents of `dist/`. Asset paths are relative, so a repository
subdirectory URL works as well as a domain root. Preserve `data/`, `docs/`,
`NOTICE.md`, `LICENSE` and the per-image notices when redistributing.
