import re
import os

def check_brackets():
    html_path = "../frontend/index.html"
    if not os.path.exists(html_path):
        print(f"Error: {html_path} does not exist!")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the babel script
    pattern = re.compile(r'<script type="text/babel">(.*?)</script>', re.DOTALL)
    matches = pattern.findall(content)
    if not matches:
        print("Error: No <script type=\"text/babel\"> found!")
        return

    script_content = matches[0]
    print(f"Script block length: {len(script_content)} characters")

    # Let's check for unbalanced brackets
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    # We should skip contents inside strings (single quotes, double quotes, backticks)
    # and skip comments (single line // and multi-line /* */)
    i = 0
    length = len(script_content)
    lines_char_count = []
    curr_line = 1
    curr_col = 1
    
    # Pre-calculate line and column for each index
    line_col = []
    for char in script_content:
        line_col.append((curr_line, curr_col))
        if char == '\n':
            curr_line += 1
            curr_col = 1
        else:
            curr_col += 1

    in_string = None
    in_comment = None
    
    while i < length:
        char = script_content[i]
        line, col = line_col[i]

        # Handle comments
        if in_comment == 'single':
            if char == '\n':
                in_comment = None
            i += 1
            continue
        elif in_comment == 'multi':
            if char == '*' and i + 1 < length and script_content[i+1] == '/':
                in_comment = None
                i += 2
            else:
                i += 1
            continue

        # Handle string literals
        if in_string:
            if char == '\\':
                i += 2  # skip escaped char
                continue
            if char == in_string:
                in_string = None
            i += 1
            continue

        # Start of comments or strings
        if char == '/' and i + 1 < length and script_content[i+1] == '/':
            in_comment = 'single'
            i += 2
            continue
        if char == '/' and i + 1 < length and script_content[i+1] == '*':
            in_comment = 'multi'
            i += 2
            continue
        if char in ["'", '"', '`']:
            in_string = char
            i += 1
            continue

        # Check brackets
        if char in mapping.values():
            stack.append((char, line, col, i))
        elif char in mapping.keys():
            if not stack:
                print(f"Error: Unmatched closing bracket '{char}' at line {line}, col {col}")
                # Print context
                start_idx = max(0, i - 50)
                end_idx = min(length, i + 50)
                print("Context around error:")
                print(script_content[start_idx:end_idx])
                return
            else:
                top, top_line, top_col, top_idx = stack.pop()
                if top != mapping[char]:
                    print(f"Error: Mismatched bracket. Found '{char}' at line {line}, col {col} but expected closing for '{top}' from line {top_line}, col {top_col}")
                    print("Context around opening:")
                    print(script_content[max(0, top_idx - 50):min(length, top_idx + 50)])
                    print("Context around closing:")
                    print(script_content[max(0, i - 50):min(length, i + 50)])
                    return

        i += 1

    if stack:
        print(f"Error: {len(stack)} unclosed brackets left at the end of the script!")
        for bracket, line, col, idx in reversed(stack):
            print(f"Unclosed '{bracket}' from line {line}, col {col}")
            print("Context:")
            print(script_content[max(0, idx - 40):min(length, idx + 40)])
            print("-" * 20)
            break # just print the first one
    else:
        print("Success: All basic brackets (), {}, [] are balanced!")

if __name__ == "__main__":
    check_brackets()
