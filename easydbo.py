import sys
from easydbo.output.log import Log

if len(sys.argv) == 1:
    from easydbo.main.gui.main import main
    main()
    exit()

argv1 = ['delete', 'excel', 'insert', 'select', 'update']
if len(sys.argv) < 2 or sys.argv[1] not in argv1:
    Log.error(f"Argument1 must be {str(argv1)[1:-1]}, or '{argv1[-1]}'")

operation = sys.argv[1]
sys.argv.remove(operation)
if operation == 'select':
    from easydbo.main.select.facade import facade
    facade()
else:
    from easydbo.main.modify.facade import facade
    facade(operation)
