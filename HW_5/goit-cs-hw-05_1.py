import asyncio
import aiofiles
import shutil
import logging
import argparse
from pathlib import Path

# setup the logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def copy_file(file_path: Path, output_folder: Path):
    # copy the file to the output folder with the same name as the original file has the extension
    try:
        ext = file_path.suffix.lstrip('.') or 'unknown'
        target_dir = output_folder / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_path.name

        # make asychronous flow for copying the file
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, file_path, target_path)

        logging.info(f'The file {file_path} was copied to {target_path}')
    except Exception as e:
        logging.error(f'Error copying file {file_path}: {e}')

async def read_folder(source_folder: Path, output_folder: Path):
    # read all files in the source folder
    tasks = []
    for file_path in source_folder.rglob('*'):
        if file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))

    await asyncio.gather(*tasks)

async def main():
    source_path = input('Input the path to the source folder: ')
    output_path = input('Input the path to the output folder: ')

    source_folder = Path(source_path)
    output_folder = Path(output_path)


    # parser = argparse.ArgumentParser(description='Asynchronous sorting of files by extensions.')
    # parser.add_argument('source', type=str, help='Path to the source folder')
    # parser.add_argument('output', type=str, help='Path to the output folder')
    #
    # args = parser.parse_args()
    # source_folder = Path(args.source)
    # output_folder = Path(args.output)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(f'The source folder {source_folder} does not exist or is not a directory')
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    await read_folder(source_folder, output_folder)

if __name__ == '__main__':
    asyncio.run(main())


