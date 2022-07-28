# Copyright 2022 Seth Kitchens.

from typing import Iterable
import math

from src.gp.text.table_list import TableList


__all__ = [
    'PrintColumn'
]

cmd_width = 120


class PrintColumn:

    def __init__(self, num_fields=1) -> None:
        self.rows = []
        self.num_fields = num_fields if num_fields > 0 else 0

    def __getitem__(self, index):
        return self.rows[index]

    def __setitem__(self, index, value):
        self.rows[index] = value

    def add_row(self, row):
        if self.num_fields:
            fields = []
            for field in row:
                fields.append(str(field))
            self.rows.append(fields)
        else:
            self.rows.append(str(row))

    def add_rows(self, rows):
        for row in rows:
            if isinstance(row, Iterable) and not isinstance(row, str):
                self.add_row(row)
            else:
                self.add_row([row])

    def add_blank_row(self):
        row = []
        for i in range(self.num_fields):
            row.append('')
        self.add_row(row)

    def add_dict(self, d):
        for k, v in d.items():
            self.add_row([k, v])

    def print(self):
        for row in self.rows:
            print(row)

    def print_section(columns: list, max_table_width=cmd_width, sep=' | '):
        """
        ---
        Print PrintColumn objects side-by-side
        
        ---
        Args:
            columns: list of PrintColumn objects
        """
        longest_col = 0
        for col in columns:
            if len(col.rows) > longest_col:
                longest_col = len(col.rows)
        for col in columns:
            for i in range(longest_col - len(col.rows)):
                col.add_blank_row()

        column_count = len(columns)
        row_count = len(columns[0].rows)
        tl_rows = []
        for i_row in range(row_count):
            tl_row = []
            for i_col in range(column_count):
                if columns[i_col].num_fields:
                    for field in columns[i_col][i_row]:
                        tl_row.append(field)
                else:
                    tl_row.append(columns[i_col][i_row])
            tl_rows.append(tl_row)
        
        # Create Borders between columns
        field_counts = []
        for pcol in columns:
            if pcol.num_fields:
                field_counts.append(len(pcol.rows[0]))
            else:
                field_counts.append(1)
        sep_before_indices = []
        i = 0
        for field_count in field_counts:
            i += field_count
            sep_before_indices.append(i)
        sep_before_indices.pop()
        
        # format columns
        tl = TableList(field_border_l='', field_border_r='', sep=sep, 
            sep_before_indices=sep_before_indices)
        for tl_row in tl_rows:
            tl.add_row(tl_row)
        tl.trim_longest(max_table_width)
        tl.print()

    def split_print_section(self,
            column_count,
            max_table_width=cmd_width,
            split_type='alternate',
            sep=' | '):
        """
        ---
        Split the column into multiple columns, then print them side-by-side
        
        ---
        Args:
            column_count: number of columns to split into
            split_type: alternate/divide
                alternate: every other row
                divide: divide evenly
        """
        columns = []
        row_count = len(self.rows)

        # create PrintColumns to split into
        for i in range(column_count):
            columns.append(PrintColumn(num_fields=self.num_fields))
            current = 0
            r = range(row_count)
        
        # split columns
        if split_type == 'alternate':
            for i in r:
                columns[i % column_count].add_row(self.rows[i])
                current = (current + 1) % column_count
        elif split_type == 'divide':
            rows_per_col = math.ceil(row_count / column_count)
            for i in r:
                columns[int(i / rows_per_col)].add_row(self.rows[i])
        
        return PrintColumn.print_section(columns, max_table_width=max_table_width, sep=sep)
