import atexit
import csv
import string
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta
import time


def clean_filename(filename):
    """
    Converts a string to a valid windows compliant filename
    :param filename:
    :return:
    """
    # replace spaces
    filename = filename.replace(" ", "_")

    # keep only valid ascii chars
    cleaned_filename = (
        unicodedata.normalize("NFKD", filename).encode("ASCII", "ignore").decode()
    )

    # keep only whitelisted chars
    char_limit = 255
    whitelist = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = "".join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print(
            """
              Warning:
              Filename truncated because it was over {}. Filename's may no longer be unique.
              """.format(
                char_limit
            )
        )

    return cleaned_filename[:char_limit]


class CSVLogger:
    """Helper class to manage logging to a CSV"""

    __file = None
    __writer = None
    header_placed = False

    def __init__(self, path, persistent_file=False):
        self.path = path
        self.persistent_file = persistent_file  # File connection kept open when true
        self.header_placed = True if self.path.exists() else False

    @property
    def _file(self):
        """
        Returns the open _file object
        :return:
        """
        if not self.__file:
            self.__file = open(self.path, "a+", newline="")

        return self.__file

    @property
    def _writer(self):
        """
        Returns the file writer
        :return:
        """
        if not self.__writer:
            self.__writer = csv.writer(
                self._file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )

        return csv.writer(
            self._file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

    def _write(self, data):
        """
        Handles writing to the file, and closing the connection if needed
        :param data:
        :return:
        """
        self._writer.writerow(data)
        if not self.persistent_file:
            # Close file, and set values to None so they will reopen on the next log
            self.__file.close()
            self.__file = None
            self.__writer = None

    def log(self, log_data):
        """
        Logging function
        Creates the file and places header if file not yet created
        :param log_data:
        :return:
        """
        if not self.header_placed:
            self._write(log_data.keys())
            self.header_placed = True

        self._write(log_data.values())


class NamingProject:
    """Base project class, tracking project details and location"""

    def __init__(self, project_name, project_dir=None):
        self.project_name = project_name
        self.project_stem = clean_filename(self.project_name)
        self.project_dir = Path(project_dir) if project_dir else Path.cwd().joinpath(self.project_stem)

        # Create the project folder if it does not exist
        self.project_dir.mkdir(exist_ok=True)


class SkuLogger:
    """Track a current SKU for logging"""

    project = None  # Project object

    __current_sku = None
    current_file_stem = None  # What the _file should be named
    current_timestamp = None

    skus_logged = 0  # count of SKUs logged this session

    log_file_type = "csv"

    end_flag = "***END***"
    end_strings = [
        "",
        "break",
        "end",
        "exit",
        end_flag,
    ]  # Strings that will end the sku_logger
    end = False  # Indicates if the script should end

    def __init__(self, project):
        self.project = project
        self.log_file_path = self.project.project_dir.joinpath(
            f"{self.project.project_stem}_sku_log.{self.log_file_type}"
        )

        self.logger = CSVLogger(self.log_file_path)

        # Register a method to run when script is ended
        # Cases this obj to persist through the end of the script
        atexit.register(self.cleanup)

    def cleanup(self):
        """
        Cleanup method to insert ending flag in log on exit
        :return:
        """
        try:
            if not self.end and self.skus_logged > 0:
                self.current_sku = self.end_flag
                self.log()
                print(f"Updated log with end flag: '{self.end_flag}'.")
        except:
            print(
                "An exception occurred when attempting to insert the ending tag in the log _file.\n"
                "The renaming script will assume the end-time for your last SKU is the time you run the rename script,"
                "or the next product in the log if one exists."
            )

    def log(self):
        """
        Write the current SKU info to the log _file
        :return:
        """
        print_log = f"{self.skus_logged} [{self.current_timestamp}] {self.current_sku}"
        print_log += (
            f" ({self.current_file_stem})"
            if self.current_file_stem != self.current_sku
            else ""
        )
        print(print_log)

        self.logger.log(
            {
                "timestamp": self.current_timestamp,
                "sku": self.current_sku,
                "file_stem": self.current_file_stem,
            }
        )

    @property
    def as_time_interval(self):
        """
        Converts SKU log data into a list of dicts with start and end times
        :return:
        """
        if not self.log_file_path.exists():
            print(f"There's no _file at '{self.log_file_path}")
        else:
            time_dict = []

            with open(self.log_file_path, "r") as file:
                reader = csv.reader(file)
                data = list(map(list, reader))
                row_count = len(data) - 1

                for i, x in enumerate(data):
                    if (
                        i > 0 and x[1] != self.end_flag
                    ):  # Skip header and don't return ending flags
                        timestamp = datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S.%f")
                        sku = x[1]
                        stem = x[2]

                        end_time = (
                            datetime.strptime(data[i + 1][0], "%Y-%m-%d %H:%M:%S.%f")
                            if i < row_count
                            else datetime.now()
                        )

                        time_dict.append(
                            {
                                "sku": sku,
                                "start_time": timestamp,
                                "end_time": end_time,
                                "stem": stem,
                            }
                        )

            return time_dict

    @property
    def current_sku(self):
        """
        Returns the current SKU
        :return:
        """
        return self.__current_sku

    @current_sku.setter
    def current_sku(self, sku):
        """
        Sets the current SKU value and the the windows compliant current_file_stem value
        :param sku:
        :return:
        """
        self.current_timestamp = datetime.now()

        self.end = (
            True if sku.lower() in self.end_strings else False
        )  # register exit when flag passed

        self.__current_sku = sku if not self.end else self.end_flag
        self.current_file_stem = clean_filename(self.__current_sku)

        self.skus_logged += 1

    def run(self):
        """
        Start accepting SKU inputs
        :return:
        """
        while True:
            self.current_sku = input("Current SKU: ")
            if not self.end:
                self.log()
            else:
                break


class FileRename:

    project = None  # NamingProject obj
    files_dir = None  # Location of the files to rename
    recursive = False  # Look for files recursively to rename
    sku_logger = None

    log_file_path = None
    log_file_type = "csv"
    logger = None  # CSVLogger obj

    files = None  # Files to rename

    def __init__(self, project, files_dir, recursive=False, offset=None):
        self.project = project
        self.files_dir = Path(files_dir)
        self.recursive = recursive
        self.sku_logger = SkuLogger(project)
        self.offset = timedelta(seconds=float(offset)) if offset else offset

        self.log_file_path = self.project.project_dir.joinpath(
            f"{self.project.project_stem}_rename_log.{self.log_file_type}"
        )
        self.logger = CSVLogger(self.log_file_path)

        if self.recursive:
            self.files = [f for f in self.files_dir.glob("**/*") if f.is_file()]
        else:
            self.files = [f for f in self.files_dir.iterdir()]

    def get_sku_by_timestamp(self, timestamp):
        """
        Locates the sku based on the files last modified timestamp
        :param timestamp:
        :return:
        """
        for sku_record in self.sku_logger.as_time_interval:
            if sku_record["start_time"] <= timestamp <= sku_record["end_time"]:
                return sku_record

    def run(self):
        existing_files = self.files.copy()  # List of existing files in the dir

        for file in self.files:
            # Locate record
            file_timestamp = datetime.fromtimestamp(file.lstat().st_mtime)
            if self.offset:
                file_timestamp += self.offset
            sku_record = self.get_sku_by_timestamp(file_timestamp)

            # Rename _file according to SKU
            if sku_record:
                # assemble new file name
                rename_path = file.with_name(sku_record["stem"] + file.suffix)
                # Add a number to the filename if the file already exists
                count = 0
                while rename_path in existing_files:
                    rename_path = file.with_name(
                        sku_record["stem"] + f" ({count})" + file.suffix
                    )
                    count += 1
                existing_files.append(rename_path)

                self.logger.log(
                    {
                        "timestamp": datetime.now(),
                        "sku": sku_record["sku"],
                        "original_path": file,
                        "renamed_path": rename_path,
                    }
                )

                file.rename(rename_path)
                print(f"Renamed: {file.name} >>> {rename_path.name}")


class Clock:
    def __init__(self, sleep=0.04):
        while True:
            now = datetime.now()
            print("Photograph the following value with your camera: ", now, end="\r")
            # print("This can be inserted into the offset-calc as:")
            # print(f"-y {now.year} -m {now.month} -d {now.day} -h {now.hour} -M {now.minute} -s {now.second} -f {now.microsecond}")
            # print(datetime.now(), end="\r")
            time.sleep(sleep)


class OffsetCalculator:

    def __init__(self, image_path, timestamp):
        self.image_path = Path(image_path)
        self.file_timestamp = file_timestamp = datetime.fromtimestamp(self.image_path.lstat().st_mtime)
        self.input_timestamp = input_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

        self.offset = input_timestamp - file_timestamp

    @property
    def as_seconds(self):
        return self.offset.total_seconds()
