from prettytable import PrettyTable

table = PrettyTable()
table.title = 'title'
table.add_row(['col1', 'col2'])
print(table)