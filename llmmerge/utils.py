import ast
import difflib
from typing import Dict, List, Optional, NamedTuple
import argparse

class DiffResult(NamedTuple):
    """Structure to hold different components of diff analysis"""
    header: str
    changes: List[Dict[str, str]]
    summary: str
    full_output: str

class SimpleASTAnalyzer:
    """Simple AST analyzer that avoids recursion issues"""
    
    def get_line_context(self, source_code: str) -> Dict[int, Dict[str, str]]:
        """Get context for each line without deep recursion"""
        context = {}
        
        try:
            tree = ast.parse(source_code)
            lines = source_code.split('\n')
            
            # Initialize all lines with basic info
            for i, line in enumerate(lines, 1):
                context[i] = {
                    'content': line,
                    'function': None,
                    'class': None,
                    'scope': 'module'
                }
            
            # Simple iteration through AST nodes (no recursion)
            for node in ast.walk(tree):
                if not hasattr(node, 'lineno'):
                    continue
                
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', node.lineno)
                
                if isinstance(node, ast.ClassDef):
                    for line_num in range(start_line, end_line + 1):
                        if line_num in context:
                            context[line_num]['class'] = node.name
                            context[line_num]['scope'] = 'class'
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for line_num in range(start_line, end_line + 1):
                        if line_num in context:
                            context[line_num]['function'] = node.name
                            context[line_num]['scope'] = 'function'
            
            return context
            
        except SyntaxError as e:
            print(f"Warning: Syntax error in file - {e}")
            # Return basic context for all lines
            lines = source_code.split('\n')
            for i, line in enumerate(lines, 1):
                context[i] = {
                    'content': line,
                    'function': None,
                    'class': None,
                    'scope': 'module'
                }
            return context

class FileDiffAnalyzer:
    """Simple file difference analyzer with AST context"""
    
    def __init__(self):
        self.ast_analyzer = SimpleASTAnalyzer()
    
    def read_file(self, filepath: str) -> str:
        """Read file content safely"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def compare_files(self, old_file: str, new_file: str, context_level: int = 0) -> DiffResult:
        """Compare two files and return differences with context in structured format
        
        Args:
            old_file: Path to old version of file
            new_file: Path to new version of file  
            context_level: Level of context to show (0=current scope, 1=parent scope, 2+=entire file)
            
        Returns:
            DiffResult containing header, changes, summary, and full_output
        """
        # Read files
        old_content = self.read_file(old_file)
        new_content = self.read_file(new_file)
        
        if not old_content or not new_content:
            error_msg = "Could not read one or both files"
            return DiffResult(
                header=error_msg,
                changes=[],
                summary="",
                full_output=error_msg
            )
        
        # Get AST context for both files
        old_context = self.ast_analyzer.get_line_context(old_content)
        new_context = self.ast_analyzer.get_line_context(new_content)
        
        # Get line-by-line diff
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # Use SequenceMatcher for simpler diff
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        
        # Build header
        header_lines = [
            "Analyzing file structure...",
            f"\nComparing:",
            f"  Old: {old_file}",
            f"  New: {new_file}",
            f"  Context Level: {context_level}",
            "="*60
        ]
        header = '\n'.join(header_lines)
        
        # Process changes
        changes = []
        changes_found = False
        all_output_lines = header_lines.copy()
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
                
            changes_found = True
            
            # Create change entry
            change_entry = {
                'type': tag.upper(),
                'old_lines': f"{i1+1}-{i2}",
                'new_lines': f"{j1+1}-{j2}",
                'removed_content': "",
                'added_content': "",
                'removed_context': "",
                'added_context': ""
            }
            
            change_output_lines = []
            change_output_lines.append(f"\n{tag.upper()} at lines {i1+1}-{i2} -> {j1+1}-{j2}")
            change_output_lines.append("-" * 40)
            
            if tag in ['delete', 'replace']:
                removed_lines = []
                removed_context_lines = []
                change_output_lines.append("🔴 REMOVED:")
                contexts_shown = set()
                
                for i in range(i1, i2):
                    line_num = i + 1
                    line_content = old_lines[i]
                    ctx = old_context.get(line_num, {})
                    
                    line_str = f"  {line_num:3d}: {line_content}"
                    removed_lines.append(line_str)
                    change_output_lines.append(line_str)
                    
                    # Show full context if we haven't shown it for this function/class yet
                    context_key = (ctx.get('class'), ctx.get('function'), context_level)
                    if context_key not in contexts_shown and (ctx.get('class') or ctx.get('function') or context_level > 0):
                        contexts_shown.add(context_key)
                        context_output = self.get_full_context_string(old_content, ctx, line_num, "OLD FILE", context_level)
                        removed_context_lines.append(context_output)
                        change_output_lines.append(context_output)
                
                change_entry['removed_content'] = '\n'.join(removed_lines)
                change_entry['removed_context'] = '\n'.join(removed_context_lines)
            
            if tag in ['insert', 'replace']:
                added_lines = []
                added_context_lines = []
                change_output_lines.append("🟢 ADDED:")
                contexts_shown = set()
                
                for j in range(j1, j2):
                    line_num = j + 1
                    line_content = new_lines[j]
                    ctx = new_context.get(line_num, {})
                    
                    line_str = f"  {line_num:3d}: {line_content}"
                    added_lines.append(line_str)
                    change_output_lines.append(line_str)
                    
                    # Show full context if we haven't shown it for this function/class yet
                    context_key = (ctx.get('class'), ctx.get('function'), context_level)
                    if context_key not in contexts_shown and (ctx.get('class') or ctx.get('function') or context_level > 0):
                        contexts_shown.add(context_key)
                        context_output = self.get_full_context_string(new_content, ctx, line_num, "NEW FILE", context_level)
                        added_context_lines.append(context_output)
                        change_output_lines.append(context_output)

                change_entry['added_content'] = '\n'.join(added_lines)
                change_entry['added_context'] = '\n'.join(added_context_lines)

            # Store the formatted output for this change
            change_entry['formatted_output'] = '\n'.join(change_output_lines)
            changes.append(change_entry)
            all_output_lines.extend(change_output_lines)
        
        # Generate summary
        if not changes_found:
            summary = "No differences found!"
            all_output_lines.append(summary)
        else:
            summary = self._get_summary_string(old_lines, new_lines, old_context, new_context)
            all_output_lines.append(summary)

        # Create full output
        full_output = '\n'.join(all_output_lines)

        return DiffResult(
            header=header,
            changes=changes,
            summary=summary,
            full_output=full_output
        )
    
    def _format_context(self, ctx: Dict[str, str]) -> str:
        """Format context information for display"""
        if not ctx:
            return ""
        
        parts = []
        if ctx.get('class'):
            parts.append(f"class {ctx['class']}")
        if ctx.get('function'):
            parts.append(f"function {ctx['function']}")
        
        if parts:
            return " -> ".join(parts) + f" ({ctx.get('scope', 'unknown')})"
        else:
            return "module level"
    
    def get_full_context_string(self, source_code: str, ctx: Dict[str, str], line_num: int, file_label: str = "", level: int = 0) -> str:
        """Get the full context (function/class definition) from source code as a string
        
        Args:
            source_code: The source code to analyze
            ctx: Context dictionary for the line
            line_num: The line number to highlight
            file_label: Label for the file (e.g., "OLD FILE", "NEW FILE")
            level: Context level (0=current scope, 1=parent scope, 2=grandparent, etc.)
            
        Returns:
            String containing the formatted context
        """
        if not source_code:
            return ""
        
        output_lines = []
        lines = source_code.split('\n')
        context_lines = []
        context_desc = ""
        
        try:
            tree = ast.parse(source_code)
            
            if level >= 2:
                # Level 2+: Show entire file
                context_lines = [(i+1, line) for i, line in enumerate(lines)]
                context_desc = "entire file"
                
            elif level == 1:
                # Level 1: Show parent context (class if function is in class, or module level)
                target_class = ctx.get('class')
                target_function = ctx.get('function')
                
                if target_class and target_function:
                    # Function is in a class, show the entire class
                    for node in ast.walk(tree):
                        if (isinstance(node, ast.ClassDef) and 
                            hasattr(node, 'lineno') and node.name == target_class):
                            start_line = node.lineno
                            end_line = getattr(node, 'end_lineno', node.lineno)
                            for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                                context_lines.append((i+1, lines[i]))
                            context_desc = f"class {target_class} (parent context)"
                            break
                
                elif target_function and not target_class:
                    # Function at module level, show more module context around it
                    # Find all top-level functions and classes
                    module_items = []
                    for node in ast.walk(tree):
                        if hasattr(node, 'lineno') and isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Check if it's at module level (not nested)
                            parent_found = False
                            for parent in ast.walk(tree):
                                if (parent != node and hasattr(parent, 'lineno') and 
                                    isinstance(parent, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and
                                    parent.lineno <= node.lineno <= getattr(parent, 'end_lineno', parent.lineno)):
                                    parent_found = True
                                    break
                            if not parent_found:
                                module_items.append((node.lineno, getattr(node, 'end_lineno', node.lineno), node.name))
                    
                    # Sort by line number and show context around target function
                    module_items.sort()
                    target_idx = -1
                    for i, (start, end, name) in enumerate(module_items):
                        if name == target_function:
                            target_idx = i
                            break
                    
                    if target_idx >= 0:
                        # Show current function plus one before and one after if they exist
                        context_start = max(0, target_idx - 1)
                        context_end = min(len(module_items), target_idx + 2)
                        
                        overall_start = module_items[context_start][0]
                        overall_end = module_items[context_end - 1][1]
                        
                        for i in range(max(0, overall_start - 1), min(len(lines), overall_end)):
                            context_lines.append((i+1, lines[i]))
                        context_desc = f"module context around function {target_function}"
                
                else:
                    # Module level code, show broader module context
                    # Show 20 lines before and after the target line
                    start_line = max(1, line_num - 20)
                    end_line = min(len(lines), line_num + 20)
                    for i in range(start_line - 1, end_line):
                        context_lines.append((i+1, lines[i]))
                    context_desc = f"module context around line {line_num}"
                    
            else:
                # Level 0: Current scope (original behavior)
                target_class = ctx.get('class')
                target_function = ctx.get('function')
                
                for node in ast.walk(tree):
                    if not hasattr(node, 'lineno'):
                        continue
                    
                    # Check if this is the target class
                    if (isinstance(node, ast.ClassDef) and 
                        target_class and node.name == target_class):
                        
                        start_line = node.lineno
                        end_line = getattr(node, 'end_lineno', node.lineno)
                        
                        # If looking for a specific function within the class
                        if target_function:
                            # Find the function within this class
                            for child_node in ast.walk(node):
                                if (isinstance(child_node, (ast.FunctionDef, ast.AsyncFunctionDef)) and
                                    child_node.name == target_function):
                                    start_line = child_node.lineno
                                    end_line = getattr(child_node, 'end_lineno', child_node.lineno)
                                    break
                        
                        # Extract the context lines
                        for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                            context_lines.append((i+1, lines[i]))
                        
                        if target_function:
                            context_desc = f"function {target_function} in class {target_class}"
                        else:
                            context_desc = f"class {target_class}"
                        break
                    
                    # Check if this is the target function (not in a class)
                    elif (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                          target_function and node.name == target_function and not target_class):
                        
                        start_line = node.lineno
                        end_line = getattr(node, 'end_lineno', node.lineno)
                        
                        # Extract the function lines
                        for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                            context_lines.append((i+1, lines[i]))
                        context_desc = f"function {target_function}"
                        break
                
                # If no specific context found, show some lines around the target
                if not context_lines:
                    start_line = max(1, line_num - 5)
                    end_line = min(len(lines), line_num + 5)
                    for i in range(start_line - 1, end_line):
                        context_lines.append((i+1, lines[i]))
                    context_desc = f"lines around {line_num}"
            
            if context_lines:
                level_indicator = f"Level {level}" if level > 0 else ""
                output_lines.append(f"\n📋 FULL CONTEXT ({file_label}) {level_indicator}: {context_desc}")
                output_lines.append("─" * 80)
                
                # For very large contexts, show summary info
                if len(context_lines) > 50:
                    output_lines.append(f"    [Showing {len(context_lines)} lines - target line {line_num} highlighted]")
                
                for line_number, line_content in context_lines:
                    # Highlight the target line
                    if line_number == line_num:
                        output_lines.append(f">>> {line_number:3d}: {line_content}")
                    else:
                        output_lines.append(f"    {line_number:3d}: {line_content}")
                output_lines.append("─" * 80)
                
        except Exception as e:
            output_lines.append(f"Error extracting context: {e}")
        
        return '\n'.join(output_lines)
    
    def print_full_context(self, source_code: str, ctx: Dict[str, str], line_num: int, file_label: str = "", level: int = 0):
        """Print the full context (function/class definition) from source code
        
        This method is kept for backward compatibility but now uses get_full_context_string
        """
        context_string = self.get_full_context_string(source_code, ctx, line_num, file_label, level)
        print(context_string)
    
    def get_context_source(self, source_code: str, ctx: Dict[str, str]) -> List[str]:
        """Get the full context source lines as a list"""
        if not ctx or not source_code:
            return []
        
        lines = source_code.split('\n')
        context_lines = []
        
        try:
            tree = ast.parse(source_code)
            target_class = ctx.get('class')
            target_function = ctx.get('function')
            
            for node in ast.walk(tree):
                if not hasattr(node, 'lineno'):
                    continue
                
                # Find the appropriate node
                if (isinstance(node, ast.ClassDef) and 
                    target_class and node.name == target_class):
                    
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', node.lineno)
                    
                    # If looking for function within class
                    if target_function:
                        for child_node in ast.walk(node):
                            if (isinstance(child_node, (ast.FunctionDef, ast.AsyncFunctionDef)) and
                                child_node.name == target_function):
                                start_line = child_node.lineno
                                end_line = getattr(child_node, 'end_lineno', child_node.lineno)
                                break
                    
                    # Extract lines
                    for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                        context_lines.append(lines[i])
                    break
                
                elif (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                      target_function and node.name == target_function and not target_class):
                    
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', node.lineno)
                    
                    for i in range(max(0, start_line - 1), min(len(lines), end_line)):
                        context_lines.append(lines[i])
                    break
            
            return context_lines
            
        except Exception as e:
            print(f"Error getting context source: {e}")
            return []
    
    def _get_summary_string(self, old_lines: List[str], new_lines: List[str], 
                           old_context: Dict, new_context: Dict) -> str:
        """Get a summary as a string instead of printing"""
        output_lines = []
        
        output_lines.append(f"\n{'='*60}")
        output_lines.append("SUMMARY")
        output_lines.append(f"{'='*60}")
        output_lines.append(f"Old file: {len(old_lines)} lines")
        output_lines.append(f"New file: {len(new_lines)} lines")
        output_lines.append(f"Difference: {len(new_lines) - len(old_lines):+d} lines")
        
        # Count functions and classes
        old_functions = set()
        old_classes = set()
        new_functions = set()
        new_classes = set()
        
        for ctx in old_context.values():
            if ctx.get('function'):
                old_functions.add(ctx['function'])
            if ctx.get('class'):
                old_classes.add(ctx['class'])
        
        for ctx in new_context.values():
            if ctx.get('function'):
                new_functions.add(ctx['function'])
            if ctx.get('class'):
                new_classes.add(ctx['class'])
        
        output_lines.append(f"Functions: {len(old_functions)} -> {len(new_functions)}")
        output_lines.append(f"Classes: {len(old_classes)} -> {len(new_classes)}")
        
        # Show added/removed functions
        added_functions = new_functions - old_functions
        removed_functions = old_functions - new_functions
        
        if added_functions:
            output_lines.append(f"Added functions: {', '.join(added_functions)}")
        if removed_functions:
            output_lines.append(f"Removed functions: {', '.join(removed_functions)}")
        
        return '\n'.join(output_lines)
    
    def _print_summary(self, old_lines: List[str], new_lines: List[str], 
                      old_context: Dict, new_context: Dict):
        """Print a simple summary - kept for backward compatibility"""
        summary_string = self._get_summary_string(old_lines, new_lines, old_context, new_context)
        print(summary_string)

def extract_context(old_file, new_file, level):    
    if level < 0:
        print("Error: Context level must be 0 or greater")
        sys.exit(1)
    
    comparison = FileDiffAnalyzer().compare_files(old_file, new_file, level)

    for change_dict in comparison.changes:
        tag = change_dict['type']
        if tag in ['DELETE', 'REPLACE']:
            context = change_dict['removed_context'] 
        elif tag == 'INSERT':
            context = change_dict['added_context']
        else:
            raise ValueError("unknown change type. can only be DELETE/INSERT/REPLACE")

        context_only = context.split('\n')
        start_idx = -1
        end_idx = -1
        for line_index, string_line in enumerate(context_only):
            if string_line == '────────────────────────────────────────────────────────────────────────────────':
                if start_idx < 0:
                    start_idx = line_index
                elif end_idx < 0:
                    end_idx = line_index
                    break
        context_only = [line[4:] for line in context_only[start_idx+1:end_idx]]
        change_dict['context_only'] = '\n'.join(context_only)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Compare two Python files with AST context")
    parser.add_argument("old_file", help="Path to old version of file")
    parser.add_argument("new_file", help="Path to new version of file")
    parser.add_argument("-l", "--level", type=int, default=0, 
                        help="Context level: 0=current scope (default), 1=parent scope, 2+=entire file")
    
    args = parser.parse_args()
    
    if args.level < 0:
        print("Error: Context level must be 0 or greater")
        return
    
    analyzer = FileDiffAnalyzer()
    result = analyzer.compare_files(args.old_file, args.new_file, args.level)

    return result

# Example usage with full context printing
def example_with_full_context():
    """Example showing how to use the full context printing"""
    analyzer = FileDiffAnalyzer()
    
    old_content = analyzer.read_file("old_file.py")
    new_content = analyzer.read_file("new_file.py")
    
    if not old_content or not new_content:
        return
    
    old_context = analyzer.ast_analyzer.get_line_context(old_content)
    new_context = analyzer.ast_analyzer.get_line_context(new_content)
    
    # Example: Print full context for line 15 in old file
    line_num = 15
    if line_num in old_context:
        ctx = old_context[line_num]
        print(f"Context info for line {line_num}: {analyzer._format_context(ctx)}")
        
        # Get the full source context as string
        context_string = analyzer.get_full_context_string(old_content, ctx, line_num)
        print(context_string)
        
        # Or get context as list of strings
        context_source = analyzer.get_context_source(old_content, ctx)
        if context_source:
            print(f"\nContext source has {len(context_source)} lines")

def demo_context_extraction():
    """Demo showing different ways to extract and display context"""
    analyzer = FileDiffAnalyzer()
    
    # Sample Python code for testing
    sample_code = '''
class MyClass:
    def __init__(self):
        self.value = 0
    
    def method1(self):
        return self.value
    
    def method2(self, x):
        self.value = x
        return self.value

def standalone_function():
    print("Hello")
    return 42
'''
    
    # Get context for each line
    context_map = analyzer.ast_analyzer.get_line_context(sample_code)
    
    print("CONTEXT EXTRACTION DEMO")
    print("=" * 40)
    
    for line_num, ctx in context_map.items():
        if ctx['content'].strip():  # Skip empty lines
            print(f"\nLine {line_num}: {ctx['content']}")
            print(f"  Context: {analyzer._format_context(ctx)}")
            
            # Show full context for function/class definitions
            if 'def ' in ctx['content'] or 'class ' in ctx['content']:
                print("  Full context:")
                context_string = analyzer.get_full_context_string(sample_code, ctx, line_num)
                print(context_string)

# Function to analyze only specific types of changes
def analyze_function_changes_only(old_file: str, new_file: str):
    """Focus only on function-level changes"""
    analyzer = FileDiffAnalyzer()
    
    old_content = analyzer.read_file(old_file)
    new_content = analyzer.read_file(new_file)
    
    if not old_content or not new_content:
        return
    
    old_context = analyzer.ast_analyzer.get_line_context(old_content)
    new_context = analyzer.ast_analyzer.get_line_context(new_content)
    
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    print("FUNCTION-LEVEL CHANGES ONLY:")
    print("=" * 40)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        
        # Check if changes involve functions
        function_change = False
        
        if tag in ['delete', 'replace']:
            for i in range(i1, i2):
                if old_context.get(i+1, {}).get('scope') == 'function':
                    function_change = True
                    break
        
        if tag in ['insert', 'replace']:
            for j in range(j1, j2):
                if new_context.get(j+1, {}).get('scope') == 'function':
                    function_change = True
                    break
        
        if function_change:
            print(f"\n{tag.upper()} in function at lines {i1+1}-{i2} -> {j1+1}-{j2}")
            
            if tag in ['delete', 'replace']:
                first_function_context = None
                for i in range(i1, i2):
                    ctx = old_context.get(i+1, {})
                    if ctx.get('scope') == 'function':
                        if first_function_context is None:
                            first_function_context = ctx.get('function', 'unknown')
                        print(f"  -{i+1:3d}: {old_lines[i]}")
                if first_function_context:
                    print(f"       Context: in function {first_function_context}")
            
            if tag in ['insert', 'replace']:
                first_function_context = None
                for j in range(j1, j2):
                    ctx = new_context.get(j+1, {})
                    if ctx.get('scope') == 'function':
                        if first_function_context is None:
                            first_function_context = ctx.get('function', 'unknown')
                        print(f"  +{j+1:3d}: {new_lines[j]}")
                if first_function_context:
                    print(f"       Context: in function {first_function_context}")

if __name__ == "__main__":
    result = main()
    # Access different components
    print(result.header)

    for i, change in enumerate(result.changes):
        print(f"\nChange {i+1}: {change['type']}")
        print(f"Lines: {change['old_lines']} -> {change['new_lines']}")
        if change['removed_content']:
            print("Removed:")
            print(change['removed_content'])
        if change['added_content']:
            print("Added:")
            print(change['added_content'])

    print("============================================================\n")

    # # Or just use the full output as before
    # print("\n=== FULL OUTPUT ===")
    # print(result.full_output)

    for change_dict in result.changes:
        tag = change_dict['type']
        if tag in ['DELETE', 'REPLACE']:
            context = change_dict['removed_context'] 
        elif tag == 'INSERT':
            context = change_dict['added_context']
        else:
            print("Unknown Change Type")
            sys.exit(1)

        context_only = context.split('\n')
        start_idx = -1
        end_idx = -1
        for line_index, string_line in enumerate(context_only):
            if string_line == '────────────────────────────────────────────────────────────────────────────────':
                if start_idx < 0:
                    start_idx = line_index
                elif end_idx < 0:
                    end_idx = line_index
                    break
        context_only = [line[4:] for line in context_only[start_idx+1:end_idx]]
        print('\n'.join(context_only))

    print(result.summary)
























