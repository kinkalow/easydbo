## Easy database operation

Easy database operation (EasyDBO) is a simple GUI tool for operating MySQL.
It allows you to operate the four basic SQL instructions (SELECT, UPDATE, INSERT, and DELETE) as easily as possible.


### Requires

- MySQL >= 5.7
- Python with Tkinter
- PySimpleGUI
- mysql

<!--
### Installation

```bash
$ git clone https://github.com/kinkalow/easydbo.git
$ cd easydbo
$ pip install -r requirements.txt
$ easydbo --version  # check if the installation was successful
```
-->


### Usage

Entering `easydbo` on the command line will open MainWindow.

![MainWindow](https://raw.githubusercontent.com/kinkalow/easydbo/images/images/main.png)
<!--<img src="https://raw.githubusercontent.com/kinkalow/easydbo/images/images/main.png" width="900">-->

The table buttons are displayed at the top; human, cancer, bam, and vcf.
They are used when you want to add, update, and delete data from a table.
When you click the button, TableWindow opens (See below for details).

Under the table buttons is the Alias button.
The alias button is a shortcut for selecting data.
When you click the button, AliasWindow opens (See below for details).

Below the Alias button are the checkboxes and input texts of columns for each table.
You can use them to create SELECT statements.
More specifically, it can be described as SELECT \<columns\> FROM \<tables\> WHERE \<conditions\>.
When you check the box, you will get the values of that column.
This sets the \<columns\> of SELECT statement.
When you want to filter values, you write the condition in the input texts.
This sets the \<conditions\> of SELECT statement.
The \<tables\> is automatically created from checkboxes and input texts.
In this case, FULL OUTER JOIN is used to join tables.

When you click the Create button at the bottom, the input texts next to SELECT, FROM and WHERE will be filled with \<columns\>, \<tables\> and \<conditions\> respectively.
Then, by pressing the Query button, a SELECT statement is created from the input texts and the query is executed.
The result of that query is displayed as QueryResultWindow.
Various SELECT statements can be created by changing the values of the input texts.
If you don't need to change the values of the input texts, just click the Show button and you can see the result.
The Create button is used when you want to change the default.

Note that if the input text of SELECT, FROM, or WHERE is blank, the clause is ignored.
For example, if WHERE is blank, the query is SELECT \<columns> FROM \<tables\> \<others\>.
The \<others\> means the value of the input text under the WHERE clause.
It can be used, for example, when you want to use GROUP BY clause without WHERE word.
If SELECT, FROM, and WHERE clause are blank, the query is \<others\>.
This creates an arbitrary query.

Next is QueryResultWindow that displays the result of a query.

![QueryResultWindow](https://raw.githubusercontent.com/kinkalow/easydbo/images/images/result.png)

This is the result of checking the checkboxes for cancer_id, cancer_receive_date and bam_create_date.
The query is written at the top.
The result is displayed in tabular form at the bottom.

When you click the Save button, a window opens asking if you want to use the query as a short name (alias).
If you write a short name and click the Save button, the query and alias will be written to alias.json.
This is also reflected in AliasWindow.

Filter frame can be used to filter the results of a query.
For example, if you type 2021-01-01 in the input text under cancer_receive_date and click the Filter button, matching row data is extracted.

The buttons in all frame is used when you want to do something with every row of the query result.
Save button saves all rows as csv.
Print button displays all rows on the terminal.
GrepRun uses the grep command to display matching lines on the terminal.

The buttons in selected frame is used when you want to do something with selected row.
Save button saves selected rows as csv.
Print button displays selected rows on the terminal.

If you right-click in the table, a menu will appear and you can save and print as described above.
If you don't need save, print, and greprun, you can delete them with a config file (see easydbo.cfg for details)

The table shows the result of the query.
You can sort by clicking a column in a table
None at the end of bam_create_date means there is no corresponding value (NULL in SQL).

Next is AliasWindow that executes a query using a short name.

![AliasWindow](https://raw.githubusercontent.com/kinkalow/easydbo/images/images/alias.png)

This shows the contents of alias.json.
When you click a short name button, the corresponding SQL statement is executed and the results are displayed in the QueryResultWindow.
If the SQL statement has question mark, the SQL statement is not executed until the value is filled in for question mark
Question mark can be filled by entering a value in the input text under SQL.

So far it's about SELECT statements.
Next is how to operate INPUT, UPDATE, and DELETE statements.

![TableWindow](https://raw.githubusercontent.com/kinkalow/easydbo/images/images/table.png)

This is TableWindow when the MainWindow human button is clicked.
The Description button is column information.
This is the same as SQL `describe human`.

Below the Description button is input text of column name.
You enter a value in each input text and press the Inset button to add the value to MySQL.
Red background column must contain a value.
Blue background columns can be filled automatically or later.
When you click the red or blue columns, the CandidateWindow opens.
It shows the column values without duplicates
When you click on a value, that value is entered in the input text.

The Filter, All, and Selected frames have the same contents as described in QueryResultWindow.
The Update and Delete buttons update and delete data to MySQL.
When you select rows in the tabular and then press the Update button, the UpdateWindow opens.
When you change the values in that window and press the Update button, MySQL is also updated.
If UpdateWindow does not close automatically, the value may be entered incorrectly.
The Delete button deletes the selected row and deletes the same data in MySQL.
