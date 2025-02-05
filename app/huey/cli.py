import argparse

from app.huey.tasks import *


def main():
    parser = argparse.ArgumentParser(description="Call Huey tasks from the command line.")
    parser.add_argument("task_name", type=str, help="Name of the task to call (e.g., create_building, update_organization)")
    parser.add_argument('--kwargs', nargs='*', action=ParseKwargs, help='Named arguments for the task (e.g., --building_id=14 --name="Building A")')


    args = parser.parse_args()

    task_name = args.task_name
    task_args = args.kwargs or {} 

    task_func = globals().get(task_name)
    if not task_func:
        logger.error(f"Error: Task {task_name} not found.")
        return
    logger.info(task_args)
    logger.info(args)
    try:
        result = task_func(**task_args)
        logger.info(f"Task {task_name} called with arguments {task_args}. Result: {result}")
    except Exception as e:
        logger.exception(f"Error: Failed to execute task {task_name}. Details: {str(e)}")

class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        if values is None:
            return 
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

if __name__ == "__main__":
    main()