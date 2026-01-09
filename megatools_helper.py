"""
Helper module for locating bundled megatools executables.
Works both in development and when bundled with PyInstaller.
"""
import os
import sys
import subprocess

def get_megatools_path():
    """
    Get the path to the megatools executable.
    
    Returns:
        str: Full path to megatools.exe, or just "megatools" if using system PATH
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    # Check if bundled megatools exists
    bundled_path = os.path.join(base_path, "megatools", "megatools-1.11.3.20250401-win64", "megatools.exe")
    if os.path.exists(bundled_path):
        return bundled_path
    
    # Fallback to system PATH
    return "megatools"

def run_megatools_command(args, **kwargs):
    """
    Run a megatools command with the correct path.
    
    Args:
        args: List of command arguments (e.g., ['df', '-u', email, '-p', password])
        **kwargs: Additional arguments to pass to subprocess.run
    
    Returns:
        subprocess.CompletedProcess
    """
    megatools_exe = get_megatools_path()
    full_args = [megatools_exe] + args
    
    # Force UTF-8 encoding to prevent character display issues
    if 'encoding' not in kwargs and 'universal_newlines' in kwargs:
        kwargs['encoding'] = 'utf-8'
    
    timeout = kwargs.pop('timeout', 60) # Default 60s timeout

    try:
        if sys.platform == 'win32':
             # CREATE_NO_WINDOW is already handled by caller or via creationflags in kwargs
             # But we can enforce it if needed, though usually caller sets it.
             # subprocess.run handles basic execution.
             pass
             
        return subprocess.run(full_args, **kwargs, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Create a dummy CompletedProcess object to represent failure
        # This prevents the app from crashing but signals the failure
        return subprocess.CompletedProcess(
            args=full_args,
            returncode=1,
            stdout="",
            stderr=f"Error: Command timed out after {timeout} seconds."
        )
