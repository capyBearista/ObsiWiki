#!/usr/bin/env python3
"""
Bidirectional Sync: GitHub Wiki to Obsidian
Converts GitHub Wiki markdown back to Obsidian format and syncs to obsidian branch
"""
import sys
import re
import subprocess
from pathlib import Path
import hashlib
import json
from datetime import datetime

print("RUNNING WIKI-TO-OBSIDIAN SYNC...")

def get_current_branch():
    """Get the current git branch name"""
    return subprocess.check_output("git rev-parse --abbrev-ref HEAD",
                                 shell=True,
                                 timeout=300).decode().strip()

def get_remote_master_hash():
    """Get the latest commit hash from remote master"""
    subprocess.run("git fetch origin master", shell=True, timeout=300, check=True)
    return subprocess.check_output("git rev-parse origin/master",
                                 shell=True,
                                 timeout=300).decode().strip()

def get_local_master_hash():
    """Get the local master commit hash"""
    return subprocess.check_output("git rev-parse master",
                                 shell=True,
                                 timeout=300).decode().strip()

def load_sync_state():
    """Load the last sync state to detect external changes"""
    sync_file = Path(".obsidian_sync_state.json")
    if sync_file.exists():
        with open(sync_file, 'r') as f:
            return json.load(f)
    return {"last_master_hash": None, "last_sync_time": None}

def save_sync_state(master_hash):
    """Save the current sync state"""
    sync_state = {
        "last_master_hash": master_hash,
        "last_sync_time": datetime.now().isoformat()
    }
    with open(".obsidian_sync_state.json", 'w') as f:
        json.dump(sync_state, f, indent=2)

def has_external_changes():
    """Check if master branch has changes not from our script"""
    sync_state = load_sync_state()
    current_master_hash = get_local_master_hash()
    remote_master_hash = get_remote_master_hash()
    
    # If remote is ahead of local, we have external changes
    if current_master_hash != remote_master_hash:
        return True
    
    # If we have no previous sync state, assume external changes
    if sync_state["last_master_hash"] is None:
        return True
    
    # If master has changed since our last sync, assume external changes
    if current_master_hash != sync_state["last_master_hash"]:
        return True
        
    return False

# REVERSE CONVERSION FUNCTIONS

def reverse_page_links(m):
    """Convert GitHub Wiki page links back to Obsidian format
    [[link text|filename]] -> [[filename|link text]]
    """
    prefix = m.group(1) if m.group(1) else ""
    linktext = m.group(2)
    # Convert hyphens back to spaces in filename
    filename = m.group(3).replace("-", " ")
    sub = f"{prefix}[[{filename}|{linktext}]]"
    print(f"Page link: {m.group(0)} -> {sub}")
    return sub

def reverse_header_links(m):
    """Convert GitHub Wiki header links back to Obsidian format
    [custom display text](#some-header) -> [[#Some Header|custom display text]]
    """
    linktext = m.group(1)
    # Convert hyphenated header back to normal case
    header = m.group(2).replace("-", " ").title()
    sub = f"[[#{header}|{linktext}]]"
    print(f"Header link: {m.group(0)} -> {sub}")
    return sub

def reverse_image_links(m):
    """Convert GitHub Wiki image links back to Obsidian format
    [[image.png]] -> ![[image.png]] (only for actual image files)
    """
    prefix = m.group(1) if m.group(1) else ""
    link_content = m.group(2)
    
    # Extract filename from the link
    filename_match = re.match(r'\[\[([^\]]+)\]\]', link_content)
    if filename_match:
        filename = filename_match.group(1)
        # Check if it's likely an image file
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp']
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            sub = f"{prefix}!{link_content}"
            print(f"Image link: {m.group(0)} -> {sub}")
            return sub
    
    # If not an image, leave as is
    return m.group(0)

def apply_reverse_conversions(file_path):
    """Apply all reverse conversions to a file"""
    original_text = file_path.read_text(encoding='utf-8')
    newtext = original_text
    
    # 1. Reverse page links: [[link text|filename]] -> [[filename|link text]]
    # Pattern matches: [[text|filename]] but not image links
    newtext = re.sub(r'([^!]?)\[\[([^|\]]+)\|([^|\]]+)\]\]', reverse_page_links, newtext)
    
    # 2. Reverse header links: [text](#header) -> [[#Header|text]]
    # Pattern matches: [text](#header-with-hyphens)
    newtext = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', reverse_header_links, newtext)
    
    # 3. Reverse image links: [[image.ext]] -> ![[image.ext]]
    # Only convert if it's actually an image file
    newtext = re.sub(r'([^!]?)(\[\[[^\]]+\.(png|jpg|jpeg|gif|svg|webp|bmp)[^\]]*\]\])', 
                    reverse_image_links, newtext, flags=re.IGNORECASE)
    
    if newtext != original_text:
        print(f"Converting: {file_path}")
        file_path.write_text(newtext, encoding='utf-8')
        return True
    return False

def sync_from_wiki():
    """Main sync function: pull changes from GitHub Wiki and convert to Obsidian format"""
    
    # Check if we're in the right repository structure
    if not Path(".git").exists():
        print("Error: Not in a git repository")
        sys.exit(1)
    
    # Ensure we have the required branches
    branches = subprocess.check_output("git branch -a", shell=True).decode()
    required_branches = ['obsidian', 'ob_to_gh', 'master']
    for branch in required_branches:
        if branch not in branches:
            print(f"Error: Required branch '{branch}' not found")
            sys.exit(1)
    
    # Check for external changes
    if not has_external_changes():
        print("No external changes detected on master branch")
        return
    
    print("External changes detected! Starting reverse sync...")
    
    # Store current branch
    original_branch = get_current_branch()
    
    try:
        # 1. Pull latest changes from remote master
        subprocess.run("git checkout master", shell=True, timeout=300, check=True)
        subprocess.run("git pull origin master", shell=True, timeout=300, check=True)
        
        # 2. Get list of changed files
        # Compare with the last known state or previous commit
        sync_state = load_sync_state()
        if sync_state["last_master_hash"]:
            # Get files changed since last sync
            changed_files_output = subprocess.check_output(
                f"git diff --name-only {sync_state['last_master_hash']} HEAD",
                shell=True, timeout=300
            ).decode().strip()
        else:
            # If no previous state, get all .md files
            changed_files_output = subprocess.check_output(
                "find . -name '*.md' -not -path './.git/*'",
                shell=True, timeout=300
            ).decode().strip()
        
        if not changed_files_output:
            print("No markdown files changed")
            save_sync_state(get_local_master_hash())
            return
        
        changed_files = [Path(f) for f in changed_files_output.split('\n') if f.strip()]
        md_files = [f for f in changed_files if f.suffix == '.md' and f.is_file()]
        
        if not md_files:
            print("No markdown files to process")
            save_sync_state(get_local_master_hash())
            return
        
        print(f"Processing {len(md_files)} changed markdown files...")
        
        # 3. Checkout obsidian branch
        subprocess.run("git checkout obsidian", shell=True, timeout=300, check=True)
        
        # 4. Copy changed files from master and apply reverse conversions
        converted_files = []
        for md_file in md_files:
            # Copy file from master
            subprocess.run(f'git checkout master -- "{md_file}"', 
                         shell=True, timeout=300, check=True)
            
            # Apply reverse conversions
            if apply_reverse_conversions(md_file):
                converted_files.append(md_file)
        
        # 5. Commit changes to obsidian branch if any files were converted
        if converted_files:
            subprocess.run("git add --all", shell=True, timeout=300, check=True)
            
            commit_msg = f"Sync from GitHub Wiki: converted {len(converted_files)} files"
            subprocess.run(f'git commit -m "{commit_msg}"', 
                         shell=True, timeout=300, check=True)
            
            print(f"Successfully synced {len(converted_files)} files from GitHub Wiki to Obsidian format")
        else:
            print("No files needed conversion")
        
        # 6. Update sync state
        subprocess.run("git checkout master", shell=True, timeout=300, check=True)
        save_sync_state(get_local_master_hash())
        
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        sys.exit(1)
    finally:
        # Always return to original branch
        if original_branch != get_current_branch():
            subprocess.run(f"git checkout {original_branch}", 
                         shell=True, timeout=300, check=False)

if __name__ == "__main__":
    sync_from_wiki()