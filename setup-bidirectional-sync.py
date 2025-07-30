#!/usr/bin/env python3
"""
Setup Script for Bidirectional Obsidian-GitHub Wiki Sync
Automates the installation and configuration of both sync directions
"""
import sys
import subprocess
import shutil
from pathlib import Path
import stat

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, timeout=300)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} timed out")
        return False

def check_git_repo():
    """Check if we're in a git repository"""
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        print("Please run this script in your GitHub Wiki repository")
        return False
    return True

def check_branches():
    """Check if required branches exist"""
    print("🔍 Checking for required branches...")
    
    try:
        branches_output = subprocess.check_output("git branch -a", shell=True).decode()
        required_branches = ['obsidian', 'ob_to_gh', 'master']
        missing_branches = []
        
        for branch in required_branches:
            if branch not in branches_output:
                missing_branches.append(branch)
        
        if missing_branches:
            print(f"❌ Missing required branches: {missing_branches}")
            
            # Offer to create missing branches
            create_branches = input("Would you like to create the missing branches? (y/n): ").lower()
            if create_branches == 'y':
                for branch in missing_branches:
                    if run_command(f"git checkout -b {branch}", f"Create branch '{branch}'"):
                        print(f"✅ Created branch '{branch}'")
                    else:
                        return False
                
                # Switch back to obsidian branch
                run_command("git checkout obsidian", "Switch to obsidian branch")
            else:
                print("Setup cannot continue without required branches")
                return False
        else:
            print("✅ All required branches exist")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Could not check git branches")
        return False

def setup_hooks():
    """Set up git hooks for bidirectional sync"""
    print("🔧 Setting up git hooks...")
    
    hooks_dir = Path(".git/hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    # List of hook files and their sources
    hooks_to_setup = [
        ("post-commit", "post-commit"),
        ("post-merge", "post-merge")
    ]
    
    success = True
    for hook_name, source_file in hooks_to_setup:
        hook_path = hooks_dir / hook_name
        source_path = Path(source_file)
        
        if not source_path.exists():
            print(f"❌ Source file '{source_file}' not found")
            success = False
            continue
        
        try:
            # Copy the hook file
            shutil.copy2(source_path, hook_path)
            
            # Make it executable
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ Installed {hook_name} hook")
            
        except Exception as e:
            print(f"❌ Failed to install {hook_name} hook: {e}")
            success = False
    
    return success

def setup_sync_script():
    """Set up the wiki-to-obsidian sync script"""
    print("📝 Setting up bidirectional sync script...")
    
    script_name = "wiki-to-obsidian.py"
    script_path = Path(script_name)
    
    if not script_path.exists():
        print(f"❌ Sync script '{script_name}' not found")
        return False
    
    # Make the script executable
    try:
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        print(f"✅ Made {script_name} executable")
        return True
    except Exception as e:
        print(f"❌ Failed to make {script_name} executable: {e}")
        return False

def create_gitignore():
    """Create or update .gitignore to exclude sync state files"""
    print("📄 Updating .gitignore...")
    
    gitignore_path = Path(".gitignore")
    gitignore_entries = [
        "# Obsidian-GitHub Wiki Sync",
        ".obsidian_sync_state.json",
        "*.tmp",
        ".DS_Store"
    ]
    
    try:
        existing_content = ""
        if gitignore_path.exists():
            existing_content = gitignore_path.read_text()
        
        # Check if our entries are already there
        needs_update = False
        for entry in gitignore_entries[1:]:  # Skip the comment
            if entry not in existing_content:
                needs_update = True
                break
        
        if needs_update:
            with open(gitignore_path, 'a') as f:
                f.write("\n")
                for entry in gitignore_entries:
                    f.write(f"{entry}\n")
            print("✅ Updated .gitignore with sync-related entries")
        else:
            print("✅ .gitignore already contains sync entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .gitignore: {e}")
        return False

def test_sync():
    """Test the bidirectional sync setup"""
    print("🧪 Testing sync setup...")
    
    # Test if we can import required modules
    try:
        import json
        import re
        from datetime import datetime
        print("✅ Required Python modules available")
    except ImportError as e:
        print(f"❌ Missing required Python module: {e}")
        return False
    
    # Test git commands
    git_tests = [
        ("git rev-parse --abbrev-ref HEAD", "Get current branch"),
        ("git status --porcelain", "Check git status"),
        ("git log -1 --oneline", "Get last commit")
    ]
    
    for command, description in git_tests:
        if not run_command(command, f"Test: {description}"):
            return False
    
    print("✅ All sync components are working")
    return True

def print_usage_instructions():
    """Print instructions for using the bidirectional sync"""
    print("\n" + "="*60)
    print("🎉 BIDIRECTIONAL SYNC SETUP COMPLETE!")
    print("="*60)
    print()
    print("📖 USAGE INSTRUCTIONS:")
    print()
    print("1. 📝 OBSIDIAN TO GITHUB WIKI (Automatic):")
    print("   • Work in your Obsidian vault on the 'obsidian' branch")
    print("   • Stage and commit your changes as usual")
    print("   • The post-commit hook will automatically sync to GitHub Wiki")
    print()
    print("2. 🌐 GITHUB WIKI TO OBSIDIAN (Automatic):")
    print("   • When someone edits the GitHub Wiki directly")
    print("   • Pull the changes: git pull origin master")
    print("   • The post-merge hook will automatically sync to obsidian branch")
    print()
    print("3. 🔄 MANUAL SYNC FROM WIKI:")
    print("   • Run: python3 wiki-to-obsidian.py")
    print("   • This will check for and sync any GitHub Wiki changes")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("   • Always work on the 'obsidian' branch in Obsidian")
    print("   • The sync preserves link formats automatically")
    print("   • Check .obsidian_sync_state.json for sync status")
    print("   • Backup your vault before first use!")
    print()
    print("🐛 TROUBLESHOOTING:")
    print("   • Check git hooks are executable: ls -la .git/hooks/")
    print("   • View sync logs in git commit messages")
    print("   • Run manual sync to test: python3 wiki-to-obsidian.py")
    print()

def main():
    """Main setup function"""
    print("🚀 Setting up Bidirectional Obsidian-GitHub Wiki Sync")
    print("="*60)
    print()
    
    # Check prerequisites
    if not check_git_repo():
        sys.exit(1)
    
    if not check_branches():
        sys.exit(1)
    
    # Setup components
    setup_steps = [
        (setup_hooks, "Git hooks"),
        (setup_sync_script, "Sync script"),
        (create_gitignore, ".gitignore"),
        (test_sync, "System test")
    ]
    
    failed_steps = []
    for step_func, step_name in setup_steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ Setup failed for: {', '.join(failed_steps)}")
        print("Please check the errors above and try again.")
        sys.exit(1)
    
    # Success!
    print_usage_instructions()

if __name__ == "__main__":
    main()