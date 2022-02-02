#!/usr/bin/env python3
import sys
from easydbo.output.print_ import SimplePrint as SP

if len(sys.argv) == 1:
    from easydbo.main.gui.main import main
    main()
    exit()

argv1 = ['delete', 'excel', 'insert', 'select', 'update']
if len(sys.argv) < 2 or sys.argv[1] not in argv1:
    SP.error(f"Argument1 must be {str(argv1)[1:-1]}, or '{argv1[-1]}'")

operation = sys.argv[1]
sys.argv.remove(operation)
if operation == 'select':
    from easydbo.main.cli.select.gate import gate
    gate()
else:
    from easydbo.main.cli.modify.gate import gate
    gate(operation)
