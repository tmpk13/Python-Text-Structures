class TextTable:
    """Generate table from list of dicts or 2D array"""

    def __init__(self, data: (list[dict] | list[list]), headers: list[str] = None, header_padding:bool = True):
        self.data = data
        self.headers = headers or self._extract_headers()
        self.header_padding = header_padding

    def _extract_headers(self) -> list[str]:
        """Extract headers from data"""
        if not self.data:
            return []
        if isinstance(self.data[0], dict):
            return list(self.data[0].keys())
        return [f"Col{i}" for i in range(len(self.data[0]))]

    def _get_row_values(self, row: (dict | list)) -> list[str]:
        """Get row values as strings"""
        if isinstance(row, dict):
            return [str(row.get(h, "")) for h in self.headers]
        return [str(v) for v in row]

    def render(self, align: str = "left") -> list[str]:
        """
        Render table and return as list of lines
        align: left, right, center
        """
        if not self.data:
            return []

        # Calculate column widths
        col_widths = [len(h) for h in self.headers]
        for row in self.data:
            values = self._get_row_values(row)
            for i, val in enumerate(values):
                col_widths[i] = max(col_widths[i], len(val))

        # Build table
        lines = []

        # Top border
        lines.append("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")

        # Headers
        header_cells = []
        header_padding_cells = []
        for i, h in enumerate(self.headers):
            header_cells.append(self._align_text(h, col_widths[i], align))
            header_padding_cells.append(self._align_text(" ", col_widths[i], align))
        lines.append("│ " + " │ ".join(header_cells) + " │")
        if self.header_padding:
          lines.append("│ " + " │ ".join(header_padding_cells) + " │")
        

        # Header separator
        lines.append("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")

        # Data rows with dividers
        for i, row in enumerate(self.data):
            values = self._get_row_values(row)
            cells = []
            for j, val in enumerate(values):
                cells.append(self._align_text(val, col_widths[j], align))
            lines.append("│ " + " │ ".join(cells) + " │")

            # Add divider between rows (but not after last row)
            if i < len(self.data) - 1:
                lines.append("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")

        # Bottom border
        lines.append("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")

        return lines

    def _align_text(self, text: str, width: int, align: str) -> str:
        """Align text within width"""
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        return text.ljust(width)

    
class TextTables:
    def __init__(self, *tables: (list[dict] | list[list] | TextTable), inline = False):
        # Convert raw data to TextTable objects if needed
        self.tables = []
        for t in tables:
            if isinstance(t, TextTable):
                self.tables.append(t)
            else:
                self.tables.append(TextTable(t))
        self.inline = inline

    def print(self):
      if self.inline:
        print(self.group())
      else:
        for t in self.tables:
          print("\n".join(t.render("left")))


    def group(self, *tables: TextTable, spacing: int = 2, align: str = "left") -> str:
        """Render multiple tables horizontally side-by-side"""
        tables = self.tables
        
        if not tables:
            return ""

        # Render all tables
        rendered_tables = [t.render(align) for t in tables]

        # Get max height
        max_height = max(len(t) for t in rendered_tables)

        # Get widths of each table
        table_widths = [len(t[0]) if t else 0 for t in rendered_tables]

        # Pad all tables to same height
        for i, table_lines in enumerate(rendered_tables):
            while len(table_lines) < max_height:
                table_lines.append(" " * table_widths[i])

        # Combine horizontally
        gap = " " * spacing
        output_lines = []
        for row_idx in range(max_height):
            row_parts = [t[row_idx] for t in rendered_tables]
            output_lines.append(gap.join(row_parts))

        return "\n".join(output_lines)
