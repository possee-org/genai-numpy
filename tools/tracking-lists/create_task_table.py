from pathlib import Path

def create_task_table(task_list, num_columns, group_name = "Groups Names"):
    # Prepend "- [ ] " to each task
    # task_list = [f"- [ ] {task}" for task in task_list]

    # Calculate the maximum column width
    headers = [f"Group {i + 1}" for i in range(num_columns)]
    col_width = max(max(len(task) for task in task_list), max(len(header) for header in headers))

    # Calculate the number of chunks needed
    num_items_per_chunk = 10 * num_columns
    total_chunks = (len(task_list) + num_items_per_chunk - 1) // num_items_per_chunk

    # Initialize the table parts
    table_parts = []
    group_names = []
    header_count = 1

    for chunk in range(total_chunks):
        chunk_start = chunk * num_items_per_chunk
        chunk_end = min(chunk_start + num_items_per_chunk, len(task_list))
        chunk_tasks = task_list[chunk_start:chunk_end]

        # Determine the number of columns for the current chunk
        num_columns_current = min(num_columns, (chunk_end - chunk_start + 9) // 10)

        # Initialize the table header and the separator line for the current chunk
        headers = [f"Group {header_count + i}" for i in range(num_columns_current)]
        header = "| " + " | ".join(header.ljust(col_width) for header in headers) + " |"
        separator = "| " + " | ".join(["-" * col_width for _ in headers]) + " |"

        # Create rows for the current chunk
        rows = []
        for row_index in range(10):
            row = []
            for col_index in range(num_columns_current):
                task_index = row_index + col_index * 10
                if task_index < len(chunk_tasks):
                    row.append(chunk_tasks[task_index].ljust(col_width))
                else:
                    row.append(" " * col_width)
            if row:
                rows.append("| " + " | ".join(row) + " |")

        # Combine all parts of the current chunk
        table_chunk = "\n".join([header, separator] + rows)
        table_parts.append(table_chunk)

        # Add group names to the list
        group_names.extend(headers)

        # Increment the header count
        header_count += num_columns_current

    # Combine all chunks into the final table
    table = "\n\n".join(table_parts)

    # Print the group names with prepended "- [ ] "
    group_names_output = group_name + ":\n" + "\n".join([f"- [ ] {group}" for group in group_names])

    return f"{group_names_output}\n\n{table}"

# Example usage
task_list = [
    "Task 1", "Task 2", "Task 3"
]

# num_columns = 3
# table_markdown = create_task_table(task_list, num_columns)
# print(table_markdown)

def read_log_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]


def main(table_file = 'full_table.txt'):
    # Define the log directory and ensure it exists
    log_dir = Path("log")
    log_dir.mkdir(parents=True, exist_ok=True)


    # Get a list of all .log files in the log directory
    log_files = list(log_dir.glob('*.log'))

    # List of log filenames to skip (without the extension)
    skip_files = ['module_list.log',]

    # Filter out the log files to skip and sort the remaining list alphabetically by filename without the extension
    log_files = [log_file for log_file in log_files if log_file.name not in skip_files]

    # Sort them alphabetically
    log_files = sorted(log_files, key=lambda f: f.stem)

    # Move np to the end
    item_to_move = log_files.pop(0)
    log_files.append(item_to_move)

    with open(log_dir / table_file, 'w') as table:

        # Print the list of log files
        for log_file in log_files:
            table.write("\n## " + log_file.stem.replace('_', '.') + '\n')

            log_lines = read_log_file(log_file)
            task_list = log_lines

            num_columns = 5
            table_markdown = create_task_table(task_list, num_columns, log_file.stem.replace('_', '.') + "Groups")
            table.write(table_markdown + '\n')

    print(f"Task Tables created in {table_file}")

if __name__ == '__main__':
    main()