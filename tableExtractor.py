import csv
import re

INPUT_FILE = "input.csv"


def clean_cell(cell):
    if not cell:
        return ""
    cell = cell.replace("\xa0", " ")
    cell = cell.replace("�", " ")
    return cell.replace("\ufeff", "").strip()


def detect_columns(header_row):
    """Find starting index of each column based on header"""
    columns = {}

    for i, cell in enumerate(header_row):
        cell = clean_cell(cell)
        if (cell):
            print("Found ", cell, " at ", str(i))
            columns[i] = cell

    return columns

def classify_column(col_index, columns):
    """Assign column to nearest header start and return indentation"""
    for idx, name in reversed(columns.items()):
        if col_index >= idx:
            return name, col_index-idx

    return None, col_index

def get_first_content_cell(row):
    for i, c in enumerate(row):
        if clean_cell(c):
            return i, clean_cell(c)
    return None, ""

def get_cell_content(row):
    cell_content = []

    for i, c in enumerate(row):
        cleaned = clean_cell(c)
        if cleaned:
            cell_content.append((i, cleaned))

    return cell_content

def parse_onenote_csv(file_path):
    rows_out = []
    current = None

    # --- robust open ---
    def open_csv():
        for enc in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
            try:
                f = open(file_path, newline="", encoding=enc)
                f.readline()
                f.seek(0)
                print(f"Using encoding: {enc}")
                return f
            except UnicodeDecodeError:
                continue
        raise Exception("Encoding not supported")

    f = open_csv()
    reader = csv.reader(f)

    header = next(reader)
    header = [clean_cell(c) for c in header]

    columns = detect_columns(header)
    print("Detected columns:", columns)

    for row in reader:
        row = [clean_cell(c) for c in row]

        if not any(row):
            continue

        cell_content = get_cell_content(row)

        for index, content in cell_content:
            # --- New row (Time column) ---
            if index == 0 and re.match(r"\d{3,4}", content):
                # Store previously created row
                if current:
                    rows_out.append(current)

                # Initialise new row
                current = {}
                for key, name in columns.items():
                    current[name] = []

            column_type, indent_level = classify_column(index, columns)

            current[column_type].append((indent_level, content))

    if current:
        rows_out.append(current)
    
    # --- format indentation ---
    for r in rows_out:
        for t, c in r.items():
            c = format_indented(c)
            r[t].clear()
            r[t].append(c)

    return columns, rows_out


def format_indented(items):
    lines = []

    for indent_level, text in items:
        indent = "    " * indent_level
        lines.append(f"{indent}• {text}")

    return "\n".join(lines)


def to_matrix(headings, rows):
    matrix = []
    heading_row = []
    for idx, h in headings.items():
        heading_row.append(h)
    matrix.append(heading_row)

    for r in rows:
        row = []
        for idx, h in headings.items():
            row.append(r[h])
        matrix.append(row)

    return matrix

def export_to_html(matrix, output_file="output.html"):
    header = matrix[0]
    rows = matrix[1:]

    def clean_cell(cell):
        if not cell:
            return ""
        text = cell[0] if isinstance(cell, list) else cell
        return text.strip()

    def parse_bullets(text):
        """
        Convert indented bullet text into a nested tree structure.
        Returns a list of nodes: {"text": str, "children": []}
        """
        if not text:
            return []

        lines = text.split("\n")
        stack = []  # (indent_level, node)
        root = []

        for line in lines:
            if not line.strip():
                continue

            # Determine indent level (4 spaces per level)
            leading_spaces = len(line) - len(line.lstrip(" "))
            level = leading_spaces // 4

            content = line.strip().lstrip("•").strip()

            node = {"text": content, "children": []}

            # Find parent
            while stack and stack[-1][0] >= level:
                stack.pop()

            if not stack:
                root.append(node)
            else:
                stack[-1][1]["children"].append(node)

            stack.append((level, node))

        return root

    def render_list(nodes):
        """Convert tree into HTML <ul><li> structure"""
        if not nodes:
            return ""

        html = "<ul>"
        for node in nodes:
            html += f"<li>{node['text']}"
            if node["children"]:
                html += render_list(node["children"])
            html += "</li>"
        html += "</ul>"
        return html

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
<html>
<head>
<meta charset="UTF-8">
<style>
    body { font-family: Calibri, Arial, sans-serif; }
    table { border-collapse: collapse; width: 100%; }
    th, td {
        border: 1px solid #444;
        padding: 8px;
        vertical-align: top;
        text-align: left;
    }
    th { background-color: #f2f2f2; }
    ul { margin: 0; padding-left: 20px; }
</style>
</head>
<body>
<table>
""")

        # Header
        f.write("<tr>")
        for col in header:
            f.write(f"<th>{col}</th>")
        f.write("</tr>\n")

        # Rows
        for row in rows:
            f.write("<tr>")
            for cell in row:
                text = clean_cell(cell)

                if "•" in text:
                    tree = parse_bullets(text)
                    html_text = render_list(tree)
                else:
                    html_text = text.replace("\n", "<br>")

                f.write(f"<td>{html_text}</td>")
            f.write("</tr>\n")

        f.write("""
</table>
</body>
</html>
""")

# --- run ---
if __name__ == "__main__":
    headings, parsed = parse_onenote_csv(INPUT_FILE)
    matrix = to_matrix(headings, parsed)

    for row in matrix:
        print(row)

    export_to_html(matrix, "conference_notes.html")