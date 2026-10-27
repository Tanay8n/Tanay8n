# Putting this on your GitHub profile

1. On GitHub: **+ → New repository**. Name it exactly **Tanay8n** (same as your username), choose **Public**, tick **Add a README**, then click Create.
2. In that new repo: **Add file → Upload files**. Drag in these from the unzipped folder, keeping the `assets` folder as a folder:
   - `README.md`
   - `assets/hero.svg`
   - `assets/about-life.svg`
   - `assets/stack.svg`
   - `assets/id-dashboard.svg`
   - `assets/connect.svg`
   - (optional) the `licenses/` folder (font licences)
3. Commit to the main branch. Your new README replaces the starter one.
4. Open **github.com/Tanay8n** and check that all five images animate and the links under the last image open.

Don't upload the ZIP itself. The `source/` folder and `preview.html` are optional; they're only for editing.

**Editing later:** change your details in `source/identity.json`, run `python3 source/build.py` (needs `pip install fonttools brotli pillow`), and re-upload the changed SVGs. Then change `?v=1` to `?v=2` in README.md so GitHub refreshes its cache.
