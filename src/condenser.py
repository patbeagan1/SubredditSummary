import os
import subprocess
from glob import glob


class Condenser:
    '''
    Used to condense several week's worth of montages into a single image.

    This can lead to images of arbitrary size, so it should be used sparingly.
    '''

    def __init__(self, dir_output):
        self._dir_output = dir_output

    def condense(self, type_str: str, subreddit_arr):
        for i in subreddit_arr:
            sub_condensed = f"{i}-{type_str}"
            glob_of_files = glob(f"{self._dir_output}/{sub_condensed}*")
            if glob_of_files:
                aggregate_image = f"{self._dir_output}/{type_str}_{i}.jpg"
                self._create_aggregate_image(aggregate_image, glob_of_files)
                self._move_input_files(glob_of_files, sub_condensed)

    def _move_input_files(self, glob_of_files, sub_condensed):
        resolved_location = f"{self._dir_output}/resolved_{sub_condensed}"
        os.makedirs(resolved_location, exist_ok=True)
        for j in glob_of_files:
            try:
                os.rename(j, f"{resolved_location}/{os.path.basename(j)}")
            except expression as identifier:
                print(identifier)

    def _create_aggregate_image(self, aggregate_image, glob_of_files):
        args = [
                   "convert",
                   "-append"
               ] + glob_of_files + [
                   aggregate_image,
                   aggregate_image
               ]
        subprocess.run(args)
