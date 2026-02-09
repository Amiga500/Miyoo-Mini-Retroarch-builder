#!/usr/bin/env python3
"""
CSV to Recipe Converter for libretro-buildbot

Converts CSV recipe files to legacy recipe format with input validation
to prevent command injection and path traversal attacks.
"""
import sys
import csv
import re


def validate_name(name):
    """Validate core name - alphanumeric, underscore, hyphen only."""
    if not name:
        raise ValueError("Core name cannot be empty")
    if not re.match(r'^[a-zA-Z0-9_\-]+$', name):
        raise ValueError(f"Invalid core name: {name} (only alphanumeric, underscore, and hyphen allowed)")
    return name


def validate_dir(dir_path):
    """Validate directory path - prevent path traversal."""
    if not dir_path:
        raise ValueError("Directory path cannot be empty")
    # Allow "." for current directory
    if dir_path == ".":
        return dir_path
    # Prevent path traversal attempts
    if '..' in dir_path or dir_path.startswith('/'):
        raise ValueError(f"Invalid directory path: {dir_path} (path traversal attempt detected)")
    if not re.match(r'^[a-zA-Z0-9_\-/]+$', dir_path):
        raise ValueError(f"Invalid directory path: {dir_path}")
    return dir_path


def validate_url(url):
    """Validate Git URL - must be https."""
    if not url:
        raise ValueError("URL cannot be empty")
    # Only allow https git URLs for security
    # Domain part: lowercase letters, digits, hyphens, dots (no underscores per RFC 1035)
    # Path part: can include underscores
    if not re.match(r'^https://[a-zA-Z0-9\-\.]+(/[a-zA-Z0-9_\-\.]+)*\.git$', url):
        raise ValueError(f"Invalid URL: {url} (must be https:// and end with .git)")
    return url


def validate_git_branch(branch):
    """Validate git branch name."""
    if not branch:
        return ""  # Branch can be empty
    # Allow alphanumeric, underscore, hyphen, slash, dot
    if not re.match(r'^[a-zA-Z0-9_\-/\.]+$', branch):
        raise ValueError(f"Invalid git branch: {branch}")
    return branch


def validate_enabled(enabled):
    """Validate enabled field - must be YES or NO."""
    if enabled not in ['YES', 'NO', '']:
        raise ValueError(f"Invalid enabled value: {enabled} (must be YES or NO)")
    return enabled


def validate_command(command):
    """Validate command field."""
    if not command:
        return ""
    # Whitelist known command types
    valid_commands = ['GENERIC', 'CMAKE', 'GENERIC_GL', 'GENERIC_ALT']
    if command not in valid_commands:
        raise ValueError(f"Invalid command: {command} (must be one of {valid_commands})")
    return command


def validate_args(args):
    """Validate args field - prevent command injection."""
    if not args:
        return ""
    # Only allow safe characters: alphanumeric, underscore, hyphen, equals, spaces, dots
    # This prevents command substitution $(cmd), backticks, semicolons, pipes, etc.
    if not re.match(r'^[a-zA-Z0-9_=\s\-\.]+$', args):
        raise ValueError(
            f"Invalid args: {args} "
            "(only alphanumeric, underscore, hyphen, equals, spaces, and dots allowed)"
        )
    return args


def main():
    """Main function to convert CSV to recipe format."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.legacy>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            
            # Validate CSV has required columns
            required_columns = ['name', 'dir', 'url', 'git_branch', 'enabled', 'command', 'makefile', 'subdir']
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                raise ValueError(f"CSV missing required columns: {missing}")
            
            row_num = 1  # Start at 1 (after header)
            for row in reader:
                row_num += 1
                try:
                    # Validate all fields
                    name = validate_name(row.get('name', '').strip())
                    dir_path = validate_dir(row.get('dir', '').strip())
                    url = validate_url(row.get('url', '').strip())
                    git_branch = validate_git_branch(row.get('git_branch', '').strip())
                    enabled = validate_enabled(row.get('enabled', '').strip())
                    command = validate_command(row.get('command', '').strip())
                    makefile = row.get('makefile', '').strip()
                    subdir_raw = row.get('subdir', '').strip()
                    subdir = validate_dir(subdir_raw) if subdir_raw else '.'
                    args = validate_args(row.get('args', '').strip())
                    
                    # Build output line
                    fields = [name, dir_path, url, git_branch, enabled, command, makefile, subdir]
                    line = ' '.join(fields)
                    if args:
                        line += ' ' + args
                    
                    outfile.write(line.strip() + '\n')
                    
                except ValueError as e:
                    print(f"Error in row {row_num}: {e}", file=sys.stderr)
                    sys.exit(1)
        
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
