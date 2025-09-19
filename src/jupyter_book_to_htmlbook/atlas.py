import json
import logging
from pathlib import Path


def update_atlas(atlas: Path, processed_files: list, modify_file: bool = True):
    """
    If there is an atlas.json file present in the source directory,
    update it with the new files processed by the script.

    If not, note this in the log and return the files list string
    like usual

    Processed files should go between boilerplate/expected front matter
    and backmatter.
    """
    ordered_frontmatter = [
        'cover.html',
        'praise.html',
        'titlepage.html',
        'copyright.html',
        'dedication.html',
        'toc.html']
    ordered_backmatter = [
        'ix.html',
        'author_bio.html',
        'colo.html']

    try:
        with atlas.open() as f:
            atlas_json = json.load(f)

            atlas_files = atlas_json["files"]

            updated_files_list = []

            # keep frontmatter
            for file in ordered_frontmatter:
                if file in atlas_files:
                    updated_files_list.append(file)

            # add processed files
            updated_files_list.extend(processed_files)

            # add backmatter
            for file in ordered_backmatter:
                if file in atlas_files:
                    updated_files_list.append(file)

            atlas_json["files"] = updated_files_list

        if modify_file:  # write back to atlas.json
            atlas.write_text(json.dumps(atlas_json, sort_keys=True, indent=4))
            logging.info('Updated atlas.json')
            return
        else:  # or, save a bunch of opens during testing
            return atlas_json

    except FileNotFoundError:
        logging.error("Unable to find the provided atlas.json file.")
        print(", ".join(processed_files))

    except KeyError:
        logging.error("Couldn't find the 'files' element in the provided " +
                      "atlas.json file. Ensure it is not malformed.")
        print(", ".join(processed_files))
