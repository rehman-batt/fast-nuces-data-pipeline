"""Convert structured HTML tables into source-ready row passages."""


def table_passages(tables, max_chars):
    for table_index, table in enumerate(tables):
        headers = []
        pending = {}
        for row_index, row in enumerate(table['rows']):
            expanded = {}
            next_pending = {}
            for col, (cell, remaining) in pending.items():
                expanded[col] = cell
                if remaining > 1:
                    next_pending[col] = (cell, remaining - 1)
            col = 0
            for cell in row:
                while col in expanded:
                    col += 1
                for offset in range(cell['colspan']):
                    if col + offset in expanded:
                        raise ValueError('overlapping table cell spans')
                    expanded[col + offset] = cell
                    if cell['rowspan'] > 1:
                        next_pending[col + offset] = (cell, cell['rowspan'] - 1)
                col += cell['colspan']
            pending = next_pending
            if not expanded:
                continue
            if all(cell['header'] for cell in expanded.values()):
                headers.append(expanded)
                continue
            items = []
            for column, cell in sorted(expanded.items()):
                labels = []
                for header in headers:
                    label = header.get(column, {}).get('text', '').strip()
                    if label and label not in labels:
                        labels.append(label)
                label = ' / '.join(labels) or f'Column {column + 1}'
                items.append(f"{label}: {cell['text']}")
            prefix = table.get('caption', '').strip()
            text = ' | '.join(([prefix] if prefix else []) + items)
            if len(text) > max_chars:
                raise ValueError(f'table {table_index + 1} row {row_index + 1} exceeds chunk size')
            yield table_index, row_index, text
