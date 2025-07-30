# Bidirectional Syncing: Obsidian ↔ GitHub Wiki

This repository provides a complete **bidirectional sync solution** between [Obsidian](https://obsidian.md/) and [GitHub Wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis). Work seamlessly in Obsidian while automatically maintaining a public GitHub Wiki, with changes flowing both ways!

🆕 **NEW: Full Bidirectional Sync** - Changes made directly in GitHub Wiki now automatically sync back to your Obsidian vault!

This repository has a GitHub Wiki, accessible [here](https://github.com/BjornFJohansson/obsidian_git_experiment/wiki), or by clicking the **Wiki** link at the top of the page.

BTW, Obsidian can be confusing, but it's worth it! Here's a link to learn more about using it :) ([YouTube](https://youtu.be/QXIa0NAycGo?si=q2-NtNW7xvjYKZSy)).

## Key Differences Between Obsidian and GitHub Wiki
While both Obsidian and GitHub Wiki claim to use Markdown, the syntax is not quite the same,  differing in small but important ways, namely:
### WikiLinks
- Obsidian: `[[page|custom display text]]`
- GitHub Wiki: `[[custom display text|page]]`

In the WikiLinks format, Obsidian and GH Wiki use the opposite order.
This is important in Obsidian for how the GUI autocomplete these links
### Image Links
- Obsidian: `![[borb.png]]`
- GitHub Wiki: `[[borb.png]]`
### Header Links
- Obsidian: `[[#Some Header|custom display text]]`
- GitHub Wiki: `[custom display text](#some-header)`

## 🔄 Bidirectional Sync Features

### Automatic Sync in Both Directions
1. **Obsidian → GitHub Wiki** (Original functionality)
   - Edit notes in Obsidian vault
   - Commit changes on `obsidian` branch
   - Automatically converts links and pushes to GitHub Wiki

2. **GitHub Wiki → Obsidian** (NEW!)
   - Edit pages directly in GitHub Wiki
   - Pull changes or let post-merge hook trigger automatically
   - Automatically converts links back to Obsidian format
   - Updates your local `obsidian` branch

### Smart Conflict Prevention
- Tracks sync state to prevent infinite loops
- Detects whether changes came from Obsidian or GitHub Wiki
- Only syncs when external changes are detected

### Easy Setup
```bash
# One-command setup for bidirectional sync
python3 setup-bidirectional-sync.py
```

## How The Script Works
This is a Python script called "post-commit" which must be placed in the .git/hooks folder.

When committing, the post-commit Git hook is activated. Specifically, this script will only have an effect if the change is committed while in the "obsidian" branch.

Your GH Wiki will have three branches, "master", "ob_to_gh" and "obsidian" (after you create the latter two). The "master" branch is the only one that is visible online on GitHub Wiki.

On your computer, you should **always** have the "obsidian" branch checked out.

This script does this:

1. The committed filenames are listed by Git.
2. Filenames are filtered for .md extension and other extensions.
3. Check out the "ob_to_gh" branch.
4. Check out all the changed paths listed in 1. from "obsidian" branch
5. The checked-out .md files are processed to modify wiki and image links using regex.
6. The resulting changes are committed to "ob_to_gh".
7. Branch "master" is checked out.
8. "master" is merged with "ob_to_gh" using "--strategy-option theirs"
9. Changes in "master" are pushed to remote to make them visible.
10. Finally, the script checks out the obsidian branch again.

Note: "master" is being used for the main branch name as that's seemingly what GitHub Wiki uses by default for some reason.

Look [here](https://forum.obsidian.md/t/github-wiki-kinda-works-to-host-the-wiki/2980) for more background.

> [!WARNING]
> While I use this everyday to maintain [this](https://github.com/MetabolicEngineeringGroupCBMA/MetabolicEngineeringGroupCBMA.github.io/wiki) wiki, this was not tested on other use cases.
> ***Back up*** before using this on your repositories. Even better, run through the test below to make sure it works on your system first! This may not even be the best way to solve this problem.
> 
~ [BjornFJohansson](https://github.com/BjornFJohansson)

## How You Can Test It
1. Fork this repository.
2. Clone the forked repo.
3. Create the wiki on the forked repo using the **Wiki** tab.
4. Clone the created **GH Wiki**, typically in the format (*username*/*repository*.wiki.git). The clone link can also be found on the Wiki page under the sidebar on the right:

```
(bjorn311) bjorn@bjorn-ThinkPad-T450s:~/Desktop/Untitled Folder 2$ git clone https://github.com/BjornFJohansson/obsidian_git_experiment.wiki.git
Cloning into 'obsidian_git_experiment.wiki'...
remote: Enumerating objects: 178, done.
remote: Counting objects: 100% (178/178), done.
remote: Compressing objects: 100% (65/65), done.
remote: Total 178 (delta 114), reused 165 (delta 104), pack-reused 0
Receiving objects: 100% (178/178), 363.54 KiB | 1.37 MiB/s, done.
Resolving deltas: 100% (114/114), done.
(bjorn311) bjorn@bjorn-ThinkPad-T450s:~/Desktop/Untitled Folder 2$ cd obsidian_git_experiment.wiki/
(bjorn311) ✔ ~/Desktop/Untitled Folder 2/obsidian_git_experiment.wiki [master|✔]
07:29 $ git fetch --all
(bjorn311) ✔ ~/Desktop/Untitled Folder 2/obsidian_git_experiment.wiki [master|✔]
07:29 $ git branch -a
* master
  remotes/origin/HEAD -> origin/master
  remotes/origin/master
  remotes/origin/obsidian
(bjorn311) ✔ ~/Desktop/Untitled Folder 2/obsidian_git_experiment.wiki [master|✔]
07:29 $
```
Commands used: *git clone* (wiki) >> *git fetch --all* >> *git branch -a*

3. Copy the "post-commit" file from the forked GH repo to **.git/hooks** in the **GH Wiki** repo.
4. Create the branches "ob_to_gh" and "obsidian".
5. Switch to the "obsidian" branch. Add the following **Obsidian**-style links to a .md file.
```
Page: [[filename|title]]

Image: ![[image.ext]]

Header: [[#Some Header|custom display text]]
```

6. Stage and commit the changes in the "obsidian" branch and switch to "master" to observe the results. Check that the file(s) you created on the "obsidian" branch show up and make sure the contents have been transformed. If you copied the block above, it should now look something like this:
```
Page: [[title|filename]]

Image: [[image.ext]]

Header: [custom display text](#some-header)
```

7. Done!

## 🚀 Quick Start with Bidirectional Sync

### Prerequisites
- Python 3.6+ installed
- Git configured with your GitHub credentials
- An existing GitHub repository

### Setup Steps

1. **Create GitHub Wiki**
   - Go to your GitHub repository
   - Click the **Wiki** tab and create your first page

2. **Clone the Wiki Repository**
   ```bash
   git clone https://github.com/yourusername/yourrepo.wiki.git
   cd yourrepo.wiki
   ```

3. **Download Sync Scripts**
   - Download all files from this repository to your wiki folder
   - Or clone this repo and copy the files

4. **Run Automated Setup**
   ```bash
   python3 setup-bidirectional-sync.py
   ```
   
   This will:
   - ✅ Create required branches (`obsidian`, `ob_to_gh`, `master`)
   - ✅ Install git hooks for automatic syncing
   - ✅ Configure sync state tracking
   - ✅ Test the setup

5. **Configure Obsidian**
   ```bash
   git checkout obsidian
   ```
   - Open Obsidian and select "Open folder as vault"
   - Choose your wiki folder
   - Start creating notes with Obsidian syntax!

6. **Start Syncing**
   - **From Obsidian**: Commit changes on `obsidian` branch → automatically syncs to GitHub Wiki
   - **From GitHub Wiki**: Edit directly in browser → run `git pull origin master` → automatically syncs to Obsidian

### Manual Sync (Optional)
```bash
# Sync GitHub Wiki changes to Obsidian manually
python3 wiki-to-obsidian.py

# Check sync status
cat .obsidian_sync_state.json
```

## Legacy Manual Setup
For manual setup without the automated script, see the original instructions [here](LEGACY-SETUP.md).